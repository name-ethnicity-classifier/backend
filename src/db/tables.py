import datetime
from enum import Enum
from db.database import db
from sqlalchemy.dialects.postgresql import ENUM

class AccessLevel(Enum):
    ADMIN = "admin"
    FULL = "full"
    PENDING = "pending"
    RESTRICTED = "restricted"


class User(db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    signup_time = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(320), nullable=False)
    role = db.Column(db.String(32), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    consented = db.Column(db.Boolean, default=False)
    request_count = db.Column(db.Integer, default=0, nullable=False)
    names_classified = db.Column(db.Integer, default=0, nullable=False)
    usage_description = db.Column(db.String(500), nullable=False)
    access = db.Column(ENUM(*[a.value for a in AccessLevel], name="access_level"), default=AccessLevel.PENDING.value, nullable=False)
    access_level_reason = db.Column(db.String(500), default="We are currently reviewing your account access and usage description. Please check in later.", nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "signup_time": self.signup_time,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "password": self.password,
            "verified": self.consented,
            "consented": self.consented,
            "request_count": self.request_count,
            "names_classified": self.names_classified,
            "usage_description": self.usage_description,
            "access": self.access,
            "access_level_reason": self.access_level_reason
        }


class Model(db.Model):
    __tablename__ = "model"
    
    id = db.Column(db.String(40), primary_key=True, nullable=False)
    nationalities = db.Column(db.ARRAY(db.String()), nullable=False)
    accuracy = db.Column(db.Float, nullable=True)
    scores = db.Column(db.ARRAY(db.Float), nullable=True)
    is_trained = db.Column(db.Boolean, default=False, nullable=False)
    is_grouped = db.Column(db.Boolean, default=False, nullable=False)
    is_public = db.Column(db.Boolean, default=False, nullable=False)
    public_name = db.Column(db.String(40), nullable=False)
    request_count = db.Column(db.Integer, default=0, nullable=False)
    creation_time = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "accuracy": self.accuracy,
            "nationalities": self.nationalities,
            "scores": self.scores,
            "is_trained": self.is_trained,
            "is_grouped": self.is_grouped,
            "is_public": self.is_public,
            "public_name": self.public_name,
            "request_count": self.request_count,
            "creation_time": self.creation_time,
        }


class UserToModel(db.Model):
    __tablename__ = "user_to_model"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    model_id = db.Column(db.String(40), db.ForeignKey("model.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    request_count = db.Column(db.Integer, default=0, nullable=False)
    name = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String(512), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "model_id": self.model_id,
            "user_id": self.user_id,
            "request_count": self.request_count,
            "name": self.name,
            "description": self.description
        }


class UserQuota(db.Model):
    __tablename__ = "user_quota"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc), nullable=False)
    name_count = db.Column(db.Integer, default=0, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "last_updated": self.last_updated,
            "name_count": self.name_count
        }
