# tests/test_checkin.py
from models import Event, Attendance
from datetime import datetime, timedelta
from extensions import db

def test_event_checkin(client, login_ca):
    future = datetime.now() + timedelta(days=1)
    event = Event(
        title="Checkin Event",
        description="Test",
        event_type="Hall Chat",
        location="Room",
        start_time=future,
        end_time=future + timedelta(hours=1),
        host_ca_id=login_ca.id
    )
    db.session.add(event)
    db.session.commit()

    res = client.post(f"/event/{event.id}/checkin", data={
        "email": "student@test.com"
    }, follow_redirects=True)

    assert b"Attendance recorded" in res.data
