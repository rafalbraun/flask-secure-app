from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_bcrypt import Bcrypt
from sqlalchemy.sql import func

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=False)

    def create_reset_token(self, expires_sec=1):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=3600, salt='custom-salt', algorithm_name='HS256')
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'], salt='custom-salt')
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
