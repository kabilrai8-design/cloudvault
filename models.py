from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    files = db.relationship('File', backref='owner', lazy=True)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    original_name = db.Column(db.String(200), nullable=False)
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(50))
    share_token = db.Column(db.String(100), unique=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, nullable=True)
    download_count = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)