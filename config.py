import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config: 
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'mulevents.db')
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'images')
    QRCODE_FOLDER = os.path.join(basedir, 'static', 'qrcodes')
    