import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_hard_to_guess_string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    MAIL_SERVER = 'sandbox.smtp.mailtrap.io'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "ac54914d668b17" ##os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = "f8b0a4876f9b06" ##os.environ.get('EMAIL_PASS')
