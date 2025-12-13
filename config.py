import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config: 
    uri = os.environ.get("DATABASE_URL")
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = uri or "sqlite:///mulevents.db"
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'images')
    QRCODE_FOLDER = os.path.join(basedir, 'static', 'qrcodes')