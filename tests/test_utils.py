import pytest
from datetime import datetime, timedelta
from utils import (
    generate_ics_file,
    generate_promotion_email,
    generate_forward_to_friend_email,
    generate_message_to_ca,
    change_timezome,
    generate_qr_for_event
)


# ---------------------------
# Helpers (dummy objects)
# ---------------------------

class DummyEvent:
    def __init__(self):
        self.id = 1
        self.title = "Test Event"
        self.description = "Description"
        self.location = "Room 101"
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(hours=1)


class DummyCA:
    name = "Test CA"
    email = "ca@test.com"
    building = "Test Hall"


# ---------------------------
# Existing tests (keep)
# ---------------------------

def test_generate_ics_file():
    event = DummyEvent()
    ics = generate_ics_file(event)

    assert "BEGIN:VEVENT" in ics
    assert event.title in ics
    assert event.location in ics


def test_generate_promotion_email():
    event = DummyEvent()
    ca = DummyCA()

    mail = generate_promotion_email(event, ca)

    assert "mailto:" in mail
    assert event.title in mail
    assert ca.building in mail


def test_forward_to_friend_email():
    event = DummyEvent()
    mail = generate_forward_to_friend_email(event)

    assert "mailto:" in mail
    assert event.title in mail


def test_message_to_ca():
    event = DummyEvent()
    ca = DummyCA()

    mail = generate_message_to_ca(ca, event)

    assert ca.email in mail
    assert event.title in mail


def test_change_timezone():
    t = datetime(2025, 1, 1, 12, 0)
    utc = change_timezome(t)

    assert utc.tzinfo is not None


# ---------------------------
# NEW TEST → covers QR code
# ---------------------------

def test_generate_qr_for_event(monkeypatch, app):
    """
    Fully covers generate_qr_for_event by mocking:
    - url_for
    - qrcode.QRCode
    - image save
    """

    # 1️⃣ Fake url_for
    monkeypatch.setattr(
        "utils.url_for",
        lambda *args, **kwargs: "http://127.0.0.1/event/1/checkin"
    )

    # 2️⃣ Fake QRCode object
    class FakeQR:
        def __init__(self, *args, **kwargs):
            pass

        def add_data(self, data):
            assert "checkin" in data

        def make(self, fit=True):
            pass

        def make_image(self, *args, **kwargs):
            class FakeImage:
                def save(self, path):
                    # Pretend we saved a file
                    assert "event_1.png" in path
            return FakeImage()

    monkeypatch.setattr("utils.qrcode.QRCode", FakeQR)

    # 3️⃣ Run inside Flask app context
    with app.app_context():
        filename = generate_qr_for_event(1)

    assert filename == "event_1.png"
