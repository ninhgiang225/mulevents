from extensions import db 
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable= False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_ca = db.Column(db.Boolean, default = False)
    building = db.Column(db.String(120))    
    residents_count = db.Column(db.Integer, default=0)
       
    hosted_events = db.relationship(
        'Event',
        backref='host_ca',
        foreign_keys='Event.host_ca_id'
    )

    collab_events = db.relationship(
        'Event',
        backref='collab_ca',
        foreign_keys='Event.collab_ca_id'
    )


class Event(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(200), nullable = False)
    description = db.Column(db.Text, nullable = False)
    event_type = db.Column(db.String(80), nullable = False)
    location = db.Column(db.String(80), nullable=False)
    start_time = db.Column(db.DateTime, nullable = False)

    host_ca_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    collab_ca_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    end_time = db.Column(db.DateTime, nullable = False)
    image_filename = db.Column(db.String(200))
    create_at = db.Column(db.DateTime, default=datetime.utcnow)
    attendances = db.relationship('Attendance', backref='event', lazy=True)

    def attendance_count(self):
        return len([a for a in self.attendances if a.present])


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))
    user_email=db.Column(db.String(200))
    present = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)