import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tasks.db' # I am using lite for simplicity
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your_jwt_secret_key')  # Change this!