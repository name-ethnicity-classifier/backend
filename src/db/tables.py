import datetime
from db.database import db


class User(db.Model):
    __tablename__ = "user"
    
    # Define columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    signup_time = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(320), nullable=False)
    role = db.Column(db.String(32), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    consented = db.Column(db.Boolean, default=False)

    # models = relationship("Model", secondary="user_to_model")

    def to_dict(self):
        return {
            "id": self.id,
            "signup_time": self.signup_time,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "password": self.password,
            "verified": self.consented,
            "consented": self.consented
        }


class Model(db.Model):
    __tablename__ = "model"
    
    # Define columns
    id = db.Column(db.String(40), primary_key=True, nullable=False)
    nationalities = db.Column(db.ARRAY(db.String()), nullable=False)
    accuracy = db.Column(db.Float, nullable=True)
    scores = db.Column(db.ARRAY(db.Float), nullable=True)
    is_trained = db.Column(db.Boolean, default=False, nullable=False)
    is_grouped = db.Column(db.Boolean, default=False, nullable=False)
    is_public = db.Column(db.Boolean, default=False, nullable=True)
    public_name = db.Column(db.String(40), nullable=False)
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
            "creation_time": self.creation_time,
        }


class UserToModel(db.Model):
    __tablename__ = "user_to_model"
    
    # Define columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    model_id = db.Column(db.String(40), db.ForeignKey("model.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    request_count = db.Column(db.Integer, default=0, nullable=False)
    name = db.Column(db.String(40), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "model_id": self.model_id,
            "user_id": self.user_id,
            "request_count": self.request_count,
            "name": self.name
        }
