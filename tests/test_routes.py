# tests/test_routes.py
from models import Event
from datetime import datetime, timedelta
import pytest
from extensions import db


def test_feed_page(client):
    res = client.get("/")
    assert res.status_code == 200


def test_ca_required_redirect(client, normal_user):
    client.post("/login", data={
        "email": normal_user.email,
        "password": "password"
    })
    res = client.get("/ca/create", follow_redirects=True)
    assert b"Not authorized" in res.data


def test_create_event(client, login_ca):
    future = datetime.now() + timedelta(days=1)
    data = {
        "title": "Test Event",
        "description": "Desc",
        "event_type": "Hall Chat",
        "location": "Room 101",
        "start_time": future.strftime("%Y-%m-%dT%H:%M"),
        "end_time": (future + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M"),
        "collab_ca": 0
    }

    res = client.post("/ca/create", data=data, follow_redirects=True)
    assert b"Event created successfully" in res.data


def test_delete_event(client, login_ca):
    future = datetime.now() + timedelta(days=1)
    event = Event(
        title="Delete Me",
        description="Test",
        event_type="Hall Chat",
        location="Room",
        start_time=future,
        end_time=future + timedelta(hours=1),
        host_ca_id=login_ca.id
    )
    from extensions import db
    db.session.add(event)
    db.session.commit()

    res = client.post(f"/ca/event/{event.id}/delete", follow_redirects=True)
    assert res.status_code == 200


def test_feed(client):
    res = client.get("/")
    assert res.status_code == 200


def test_event_detail_404(client):
    res = client.get("/event/999")
    assert res.status_code == 404


def test_ca_guard(client, normal_user):
    client.post("/login", data={
        "email": normal_user.email,
        "password": "password"
    })

    res = client.get("/ca/create", follow_redirects=True)
    assert b"Not authorized" in res.data

@pytest.fixture
def force_login(app, client, ca_user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(ca_user.id)
        sess["_fresh"] = True
    return ca_user

def test_ca_routes(client, force_login):
    client.get("/ca/your-events")
    client.get("/contact")
    client.get("/peak-events")



@pytest.fixture
def future_event(login_ca):
    event = Event(
        title="Future Event",
        description="Desc",
        event_type="Hall Chat",
        location="Room",
        start_time=datetime.now() + timedelta(days=1),
        end_time=datetime.now() + timedelta(days=1, hours=1),
        host_ca_id=login_ca.id
    )
    db.session.add(event)
    db.session.commit()
    return event


@pytest.fixture
def past_event(login_ca):
    event = Event(
        title="Past Event",
        description="Desc",
        event_type="Hall Chat",
        location="Room",
        start_time=datetime.now() - timedelta(days=2),
        end_time=datetime.now() - timedelta(days=2, hours=-1),
        host_ca_id=login_ca.id
    )
    db.session.add(event)
    db.session.commit()
    return event



def test_edit_event_get(client, force_login, future_event):
    res = client.get(f"/ca/event/{future_event.id}/edit")
    assert res.status_code == 200


def test_edit_event_post(client, force_login, future_event):
    data = {
        "title": "Updated",
        "description": "Updated desc",
        "event_type": "Hall Chat",
        "location": "New Room",
        "start_time": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M"),
        "end_time": (datetime.now() + timedelta(days=2, hours=1)).strftime("%Y-%m-%dT%H:%M"),
        "collab_ca": 0
    }

    res = client.post(
        f"/ca/event/{future_event.id}/edit",
        data=data,
        follow_redirects=True
    )

    assert b"Event updated successfully" in res.data


def test_delete_event_forbidden(client, normal_user, future_event):
    client.post("/login", data={
        "email": normal_user.email,
        "password": "password"
    })

    res = client.post(f"/ca/event/{future_event.id}/delete")
    assert res.status_code == 403


def test_your_event_detail(client, force_login, future_event):
    res = client.get(f"/ca/event/{future_event.id}")
    assert res.status_code == 200


def test_past_event_redirect(client, force_login, future_event):
    res = client.get(f"/ca/event/{future_event.id}/past", follow_redirects=True)
    assert res.status_code == 200


def test_past_event_detail(client, force_login, past_event):
    res = client.get(f"/ca/event/{past_event.id}/past")
    assert res.status_code == 200

def test_checkin_closed(client, past_event):
    res = client.get(f"/event/{past_event.id}/checkin", follow_redirects=True)
    assert b"Check-in is closed" in res.data

def test_duplicate_checkin(client, future_event):
    client.post(f"/event/{future_event.id}/checkin", data={"email": "a@test.com"})
    res = client.post(
        f"/event/{future_event.id}/checkin",
        data={"email": "a@test.com"},
        follow_redirects=True
    )
    assert b"already checked in" in res.data

def test_download_ics(client, future_event):
    res = client.get(f"/download_ics/{future_event.id}")
    assert res.status_code == 200
    assert res.mimetype == "text/calendar"

def test_promotion_routes(client, future_event):
    assert client.get(f"/promote_event/{future_event.id}").status_code == 302
    assert client.get(f"/refer_friend/{future_event.id}").status_code == 302
    assert client.get(f"/contact_ca/{future_event.id}").status_code == 302



