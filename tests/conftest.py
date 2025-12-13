# tests/conftest.py
import pytest

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import pytz

class TestConfig:
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret"
    UPLOAD_FOLDER = "tests/uploads"
    QRCODE_FOLDER = "tests/qrcodes"


@pytest.fixture
def app():
    app = create_app()
    app.config.from_object(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def ca_user(app):
    user = User(
        name="Test CA",
        email="ngnguy26@colby.edu",
        password=generate_password_hash("password"),
        is_ca=True,
        building="Test Hall",
        residents_count=50,
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def normal_user(app):
    user = User(
        name="Normal User",
        email="user@test.com",
        password=generate_password_hash("password"),
        is_ca=False,
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def login_ca(client, ca_user):
    client.post("/login", data={
        "email": ca_user.email,
        "password": "password"
    })
    return ca_user

@pytest.fixture(autouse=True)
def disable_templates(monkeypatch):
    monkeypatch.setattr("flask.templating._render", lambda *a, **k: "")

@pytest.fixture(autouse=True)
def disable_templates(monkeypatch):
    monkeypatch.setattr(
        "flask.templating._render",
        lambda *args, **kwargs: ""
    )