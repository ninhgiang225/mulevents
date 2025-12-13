# tests/test_auth.py
from models import User

def test_login_success(client, ca_user):
    res = client.post("/login", data={
        "email": ca_user.email,
        "password": "password"
    }, follow_redirects=True)

    assert res.status_code == 200


def test_login_failure(client):
    res = client.post("/login", data={
        "email": "wrong@test.com",
        "password": "wrong"
    }, follow_redirects=True)

    assert b"Invalid email or password" in res.data


def test_signup_blocked_email(client):
    res = client.post("/signup", data={
        "name": "Bad User",
        "email": "bad@test.com",
        "password": "123",
        "building": "Hall",
        "residents_count": 10
    })

    assert b"Email not in CA list" in res.data


def test_logout(client, login_ca):
    res = client.get("/logout", follow_redirects=True)
    assert res.status_code == 200


def test_signup_success(client):
    res = client.post("/signup", data={
        "name": "CA User",
        "email": "ngnguy26@colby.edu",
        "password": "123",
        "building": "Hall",
        "residents_count": 20
    }, follow_redirects=True)

    assert b"Account created" in res.data

def test_login_redirect(client, ca_user):
    res = client.post("/login", data={
        "email": ca_user.email,
        "password": "password"
    })

    assert res.status_code == 302