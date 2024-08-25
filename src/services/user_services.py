from flask import current_app, render_template, request
from flask_jwt_extended import create_access_token, decode_token
from flask_mail import Mail, Message
import bcrypt
from schemas.user_schema import LoginSchema, SignupSchema, DeleteUser
from db.tables import User
from db.database import db
from utils import is_strong_password, is_valid_email
from errors import CustomError, CustomError


def check_user_login(data: LoginSchema) -> str:
    """
    Checks user email and password validity
    :param data: User email and password
    """

    user = User.query.filter_by(email=data.email).first()

    if not user:
        raise CustomError(
            error_code="AUTHENTICATION_FAILED",
            message="Email or password not found.",
            status_code=401
        )

    true_password_bytes = user.password.encode("utf-8")
    user_password_bytes = data.password.encode("utf-8")
    
    successful_login = bcrypt.checkpw(user_password_bytes, true_password_bytes)
    if not successful_login:
        raise CustomError(
            error_code="AUTHENTICATION_FAILED",
            message="Email or password not found.",
            status_code=401
        )

    return user.id
    

def add_user(data: SignupSchema) -> None:
    """
    Adds a new user to the database
    :param data: User sign up data
    """

    user = User.query.filter_by(email=data.email).first()

    if user:
        raise CustomError(
            error_code="EMAIL_EXISTS",
            message=f"User with email {data.email} does already exist.",
            status_code=409
        )

    if len(data.name) < 2 or len(data.name) > 50:
        raise CustomError(
            error_code="INVALID_NAME",
            message=f"Invalid name (min. 2 characters, max. 50 characters).",
            status_code=422
        )

    if not is_valid_email(data.email):
        raise CustomError(
            error_code="INVALID_EMAIL",
            message=f"Invalid email.",
            status_code=422
        )

    if len(data.role) == 0:
        data.role = "Else"

    if len(data.password) > 100:
        raise CustomError(
            error_code="PASSWORD_TOO_LONG",
            message=f"Max password length is 100 characters.",
            status_code=422
        )

    if not is_strong_password(data.password):
        raise CustomError(
            error_code="PASSWORD_TOO_WEAK",
            message=f"Password too weak (min. 8 characters, min. 1 lower case, min. 1 upper case, min. 1 number).",
            status_code=422
        )

    if not data.consented:
        raise CustomError(
            error_code="NO_CONSENT",
            message=f"Terms of Service consent not granted.",
            status_code=422
        )

    # Check if given password matches password in database
    hashed_password = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8") 

    new_user = User(
        name=data.name,
        email=data.email,
        password=hashed_password,
        role=data.role,
        consented=data.consented
    )
    
    db.session.add(new_user)
    db.session.commit()


def delete_user(user_id: str, data: DeleteUser) -> None:
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
        raise CustomError(
            error_code="USER_DELETION_FAILED",
            message="Password incorrect.",
            status_code=401
        )

    db.session.delete(user)
    db.session.commit()


def send_verification_email(email: str) -> None:
    """
    Sends a verification email to the user
    :param email: Email to which to send
    :return: None
    """

    try:
        mail = Mail(current_app)

        token = create_access_token(email)
        confirmation_url = f"{request.base_url}/verify/{token}"

        email_subject = "Account confirmation for name-to-ethnicity.com."
        msg = Message(
            email_subject,
            recipients=[email],
            html=render_template("./src/templates/emailVerification.html", confirmation_url=confirmation_url)
        )
        mail.send(msg)
        
    except Exception as e:
        current_app.logger.error(f"Failed to send verification email. Error:\n{e}")
        raise CustomError(
            error_code="SIGNUP_FAILED",
            message="Error while sending verification email.",
            status_code=500
        )


def handle_email_verification(token: str) -> None:
    """
    Handles a click on the verification url
    :param token: JWT token which was added to the verification url
    :return: None
    """

    data = decode_token(token)
    email = data["email"]

    user = User.query.filter_by(email=email).first()
    if not user:
        raise CustomError(
            error_code="VERIFICATION_FAILED",
            message="User does not exist.",
            status_code=404
        )
    user.verified = True
    db.session.commit()