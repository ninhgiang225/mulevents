import qrcode
import os
from flask import url_for
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import pytz


def generate_qr_for_event(event_id):
    qr_data = url_for("main.checkin", event_id=event_id, _external=True)

    YOUR_LOCAL_IP = "137.146.121.228" 

    qr_data = qr_data.replace("127.0.0.1", YOUR_LOCAL_IP)
    qr_data = qr_data.replace("localhost", YOUR_LOCAL_IP)   

    qr = qrcode.QRCode(version=1, box_size=20, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    filename = f'event_{event_id}.png'
    filepath = os.path.join("static", "qrcodes", filename)
    img.save(filepath)

    return filename


def generate_ics_file(event):
    start_time = event.start_time.strftime("%Y%m%dT%H%M00")
    end_time = event.end_time.strftime("%Y%m%dT%H%M00")
    ics = f"""BEGIN:VCALENDAR
VERSINO:2.0
PRODID:-//Mulevents//EN
BEGIN:VEVENT
UID:event-{event.id}@mulevents.colby
DTSTAMP:{datetime.utcnow().strftime(("%Y%m%dT%H%M%SZ"))}
DTSTART:{start_time}
DTEND:{end_time}
SUMMARY:{event.title}
DESCRIPTION:{event.description}
LOCATION:{event.location}
END:VEVENT
END:VCALENDAR"""

    return ics


def generate_promotion_email(event, ca):
    subject = f"You're invited: {event.title}!"
    body = f"""

Hello my residents,

You're invited to a new community event hosted by your {ca.building}'s CA.

📌 {event.title}
{event.description}

🗓 When: {event.start_time.strftime('%A')}, {event.start_time.strftime('%b %d')}
🕒 Time: {event.start_time.strftime('%I:%M %p')} - {event.end_time.strftime('%I:%M %p')}
📍 Where: {event.location}

Hope to see you there !

Best,
{ca.name}
Your {ca.building}'s Community Advisor
"""
    return f"mailto:?subject={subject}&body={body.replace('\n', '%0A')}"


def generate_forward_to_friend_email(event):
    subject = f"Check out this event: {event.title}!"
    body = f"""

Hey,

I though you might like this event:

{event.title}
{event.description}

When: {event.start_time.strftime('%A')}, {event.start_time.strftime('%b %d')}, {event.start_time.strftime('%I:%M %p')}
Where: {event.location}

Want to go together?

- Sent via Mulevents
"""
    return f"mailto:?subject={subject}&body={body.replace('\n', '%0A')}"


def generate_message_to_ca(ca, event):
    subject = f"Question about {event.title}"
    body = f"""
Hi {ca.name},

I have a question about your event: {event.title}.

(Write your question here)

Thanks!
"""
    return f"mailto:{ca.email}?subject={subject}&body={body.replace('\n', '%0A')}"


def change_timezome(time):
    local_tz = pytz.timezone("America/New_York")
    time_utc = local_tz.localize(time).astimezone(pytz.UTC)

    return time_utc

    