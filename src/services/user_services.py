import traceback
from flask import current_app, request
from flask_jwt_extended import create_access_token, decode_token
import bcrypt
import resend

from schemas.user_schema import LoginSchema, SignupSchema, DeleteUserSchema
from db.tables import User, AccessLevel
from db.database import db
from utils import is_strong_password, is_valid_email
from errors import GeneralError, GeneralError


def check_user_login(data: LoginSchema):
    """
    Checks user email and password validity
    :param data: User email and password
    """

    user = User.query.filter(User.email.ilike(data.email)).first()

    if not user:
        raise GeneralError(
            error_code="AUTHENTICATION_FAILED",
            message="Email or password not found.",
            status_code=401
        )

    true_password_bytes = user.password.encode("utf-8")
    user_password_bytes = data.password.encode("utf-8")
    
    successful_login = bcrypt.checkpw(user_password_bytes, true_password_bytes)
    if not successful_login:
        raise GeneralError(
            error_code="AUTHENTICATION_FAILED",
            message="Email or password not found.",
            status_code=401
        )
    
    return user


def check_user_existence(user_id) -> User:
    """
    Checks if user with given ID exists in the database, to make sure
    that even when a user is deleted their JWT token doesn't work anymore.
    :param user_id: User id to check
    :return: User database entry if it exists
    """
    
    user = User.query.filter_by(id=user_id).first()

    if not user:
        raise GeneralError(
            error_code="AUTHENTICATION_FAILED",
            message="User does not exist.",
            status_code=401
        )
    
    return user
    

def add_user(data: SignupSchema):
    """
    Adds a new user to the database
    :param data: User sign up data
    """

    user = User.query.filter(User.email.ilike(data.email)).first()

    if user:
        raise GeneralError(
            error_code="EMAIL_EXISTS",
            message=f"User with email {data.email} does already exist.",
            status_code=409
        )

    if len(data.name) < 2 or len(data.name) > 50:
        raise GeneralError(
            error_code="INVALID_NAME",
            message=f"Invalid name (min. 2 characters, max. 50 characters).",
            status_code=422
        )

    if not is_valid_email(data.email):
        raise GeneralError(
            error_code="INVALID_EMAIL",
            message=f"Invalid email.",
            status_code=422
        )

    if len(data.role) == 0 or len(data.role) > 75:
        data.role = "Else"

    if len(data.password) > 100:
        raise GeneralError(
            error_code="PASSWORD_TOO_LONG",
            message=f"Max password length is 100 characters.",
            status_code=422
        )

    if not is_strong_password(data.password):
        raise GeneralError(
            error_code="PASSWORD_TOO_WEAK",
            message=f"Password too weak (min. 8 characters, min. 1 lower case, min. 1 upper case, min. 1 number).",
            status_code=422
        )

    if not data.consented:
        raise GeneralError(
            error_code="NO_CONSENT",
            message=f"Terms of Service consent not granted.",
            status_code=422
        )

    if len(data.usageDescription) < 40 or len(data.usageDescription) > 500:
        raise GeneralError(
            error_code="INVALID_USAGE_DESCRIPTION",
            message=f"Invalid usage description (min. 40, max. 500 characters).",
            status_code=422
        )

    hashed_password = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8") 

    send_verification_email(data.email)

    auto_verify_user = not current_app.config["USER_VERIFICATION_ACTIVE"]

    new_user = User(
        name=data.name,
        email=data.email,
        password=hashed_password,
        role=data.role,
        consented=data.consented,
        usage_description=data.usageDescription,
        verified=auto_verify_user
    )
    
    db.session.add(new_user)
    db.session.commit()


def update_usage_description(user_id: str, new_description: str):
    """
    Updates the usage description for a user
    :param user_id: ID of the user
    :param new_description: New usage description
    """
    
    user = User.query.filter_by(id=user_id).first()

    if not user:
        raise GeneralError(
            error_code="USER_NOT_FOUND",
            message="User does not exist.",
            status_code=404
        )

    if len(new_description) < 40 or len(new_description) > 500:
        raise GeneralError(
            error_code="INVALID_USAGE_DESCRIPTION",
            message="Invalid usage description (min. 40, max. 500 characters).",
            status_code=422
        )

    user.usage_description = new_description
    user.access_level_reason = "We are currently reviewing your usage description. Please check in later."
    db.session.commit()


def delete_user(user_id: str, data: DeleteUserSchema):
    """
    Deletes a user from the database
    :param user_id: ID of the user to delete
    :param data: User deletion data (contains just the confirmation password)
    """

    user = User.query.filter_by(id=user_id).first()

    true_password_bytes = user.password.encode("utf-8")
    user_password_bytes = data.password.encode("utf-8")
    
    successful_authentication = bcrypt.checkpw(user_password_bytes, true_password_bytes)
    if not successful_authentication:
        raise GeneralError(
            error_code="USER_DELETION_FAILED",
            message="Password incorrect.",
            status_code=401
        )

    db.session.delete(user)
    db.session.commit()


def send_verification_email(email: str):
    """
    Sends a verification email to the user
    :param email: Email to which to send
    """

    if not current_app.config["USER_VERIFICATION_ACTIVE"]:
        current_app.logger.warning(f"Skipping user email verification.")
        return

    try:
        token = create_access_token(email)
        confirmation_url = f"{request.url_root}/verify/{token}"

        with open("./src/templates/email-verification.html", "r") as f:
            email_template = f.read().replace("{{ confirmation_url }}", confirmation_url)

        params = {
            "from": "name-to-ethnicity <noreply@name-to-ethnicity.com>",
            "to": [email],
            "subject": "Account verification.",
            "html": email_template
        }
        email = resend.Emails.send(params)

        current_app.logger.error(f"Verification email sent (resend id: {email['id']}).")
        
    except Exception as e:
        current_app.logger.error(f"Failed to send verification email. Error:\n{traceback.format_exc()}")
        raise GeneralError(
            error_code="SIGNUP_FAILED",
            message="Error while sending verification email.",
            status_code=500
        )
 

def handle_email_verification(token: str):
    """
    Handles a click on the verification url
    :param token: JWT token which was added to the verification url
    :return: None
    """

    data = decode_token(token)
    email = data["sub"]

    user = User.query.filter_by(email=email).first()
    if not user:
        raise GeneralError(
            error_code="VERIFICATION_FAILED",
            message="User does not exist.",
            status_code=404
        )

    current_app.logger.error(f"Email verified.")

    user.verified = True
    db.session.commit()


def check_user_restriction(user_id: str):
    user = User.query.filter_by(id=user_id).first()

    if user.access.lower() == AccessLevel.PENDING.value:
        raise GeneralError(
            error_code="PENDING_ACCESS",
            message="Your account access and/or usage description is currently being reviewed before granting you access.",
            status_code=403
        )
    
    if user.access.lower() == AccessLevel.RESTRICTED.value:
        raise GeneralError(
            error_code="RESTRICTED_ACCESS",
            message=f"Since May 2025, we require users to provide a description of how they are using our service to ensure ethical compliance. Your usage description is either missing, insufficient or currently under review (see the reason below). Please update it in the user settings on our website. Reason: {user.access_level_reason}",
            status_code=403
        )
