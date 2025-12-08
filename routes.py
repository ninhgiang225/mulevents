from flask import Blueprint, render_template, request, redirect, url_for, current_app, send_file, flash, abort, send_file, make_response, Response
from models import User, Event, Attendance
from extensions import db 
from forms import EventForm
from flask_login import current_user, login_required
from utils import generate_qr_for_event, generate_forward_to_friend_email, generate_promotion_email, generate_ics_file, generate_message_to_ca, change_timezome
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import func
from werkzeug.utils import secure_filename
import os 
import pytz
import time


bp = Blueprint('main', __name__, template_folder='templates')


@bp.route('/')
def feed():
    events = Event.query.order_by(Event.start_time.asc()).all()
    return render_template('feed.html', events=events)


@bp.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    # add_calendar = generate_ics_file(event)   # generate a file in the iCalendar format
    # mailto=generate_forward_to_friend_email(event)
    return render_template('event_detail.html', event=event)


def ca_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_ca:
            flash('Not authorized', 'danger')
            return redirect(url_for('main.feed'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/ca/create', methods=['GET', 'POST'])
@login_required
@ca_required
def create_event():
    form = EventForm()

    # Populate collaborator dropdown
    active_ca = User.query.filter_by(is_ca=True).all()
    form.collab_ca.choices = [(0, "None")] + [(ca.id, ca.name) for ca in active_ca if ca.id != current_user.id]

    if request.method == "POST":
        try:
            start_time_str = request.form.get("start_time")
            end_time_str = request.form.get("end_time")

            start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M")
            end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M") 

        except Exception as e:
            flash("Invalid date format. Please re-enter.", "danger")
            print("Date parsing error:", e)
            return render_template("ca/create_event.html", form=form)
        
        if change_timezome(start_time) < datetime.now(pytz.UTC): #-1hour to give them some tolerance to create event at the spot
            flash("Start time must be in the future.", "danger")
            return render_template("ca/create_event.html", form=form)

        if end_time <= start_time:
            flash("End time must be after start time.", "danger")
            return render_template("ca/create_event.html", form=form)

        image_file = request.files.get("image")
        image_filename = None

        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            image_filename = filename

        event = Event(
            title=form.title.data,
            description=form.description.data,
            event_type=form.event_type.data,
            location=form.location.data,
            start_time=start_time,         # MUST be datetime object
            end_time=end_time,             # MUST be datetime object or None
            host_ca_id=current_user.id,
            collab_ca_id=int(form.collab_ca.data) if int(form.collab_ca.data) != 0 else None,
            image_filename=image_filename
        )

        db.session.add(event)
        db.session.commit()

        flash("Event created successfully!", "success")
        return redirect(url_for("main.event_detail", event_id=event.id))

    return render_template("ca/create_event.html", form=form)


@bp.route('/ca/event/<int:event_id>/edit', methods = ['GET', 'POST'])
@login_required
@ca_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)
    
    # Populate collaborator dropdown
    active_ca = User.query.filter_by(is_ca=True).all()
    form.collab_ca.choices = [(0, "None")] + [(ca.id, ca.name) for ca in active_ca if ca.id != current_user.id]
    
    if request.method == "GET":
        # Convert stored times to NY timezone for display in the form
        ny_tz = pytz.timezone('America/New_York')
        
        # Treat database times as naive NY times, localize them
        start_local = ny_tz.localize(event.start_time)
        end_local = ny_tz.localize(event.end_time)
        
        # Format for datetime-local input (no timezone suffix needed)
        form.start_time.data = start_local.strftime("%Y-%m-%dT%H:%M")
        form.end_time.data = end_local.strftime("%Y-%m-%dT%H:%M")
        form.collab_ca.data = event.collab_ca_id if event.collab_ca_id else 0
    
    if request.method == "POST":
        try:
            start_time_str = request.form.get("start_time")
            end_time_str = request.form.get("end_time")
            # Parse as naive datetime (user input is in NY time)
            start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M")
            end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M")
        except Exception as e:
            flash("Invalid date format. Please re-enter.", "danger")
            print("Date parsing error:", e)
            return render_template("ca/edit_event.html", form=form, event=event)
        
        # Validation (same as create_event)
        if change_timezome(start_time) < datetime.now(pytz.UTC):
            flash("Start time must be in the future.", "danger")
            return render_template("ca/edit_event.html", form=form, event=event)
        if end_time <= start_time:
            flash("End time must be after start time.", "danger")
            return render_template("ca/edit_event.html", form=form, event=event)
        
        # Handle image upload
        image_file = request.files.get("image")
        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            event.image_filename = filename
        
        # Update event fields
        event.title = form.title.data
        event.description = form.description.data
        event.event_type = form.event_type.data
        event.location = form.location.data
        event.start_time = start_time  # Store as naive datetime (NY time)
        event.end_time = end_time      # Store as naive datetime (NY time)
        event.collab_ca_id = int(form.collab_ca.data) if int(form.collab_ca.data) != 0 else None
        
        db.session.commit()
        flash("Event updated successfully!", "success")
        return redirect(url_for("main.event_detail", event_id=event.id))
    
    return render_template("ca/edit_event.html", form=form, event=event)


    
@bp.route('/ca/event/<int:event_id>/delete', methods = ['POST'])
@login_required
@ca_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id) 

    if current_user.id != event.host_ca_id and current_user.id != (event.collab_ca_id or -1): 
        abort(403)
    
    db.session.delete(event)
    db.session.commit()
    flash("Event deleted successfully!", 'success')

    return redirect(url_for("main.your_events"))


@bp.route('/ca/your-events')
@login_required
@ca_required
def your_events():
    utc_now = datetime.now(pytz.UTC)

    upcoming_events = Event.query.filter(Event.host_ca_id==current_user.id, Event.start_time > utc_now).all()
    past_events = Event.query.filter(Event.host_ca_id==current_user.id, Event.start_time <= utc_now).all()

    return render_template('ca/your_events.html', upcoming_events=upcoming_events, past_events=past_events)


@bp.route('/ca/event/<int:event_id>')
@login_required
@ca_required
def your_event_detail(event_id):
    event=Event.query.get_or_404(event_id)

    if current_user.id != event.host_ca_id and current_user.id != (event.collab_ca_id or -1): 
        abort(403)
    qr_filename = generate_qr_for_event(event_id)

    return render_template('ca/your_event_detail.html', event=event, qr_filename = qr_filename)


@bp.route('/peak-events')
def peak_events():
    month = request.args.get("month", "last")  # default to last month
    now = datetime.utcnow()

    # First day of this month
    first_day_this_month = now.replace(day=1)
    if month == "last":
        # Last month
        first_day = (first_day_this_month - timedelta(days=1)).replace(day=1)
        last_day = first_day_this_month - timedelta(days=1)
    else:
        # This month
        first_day = first_day_this_month
        # Last day of this month is optional; just use now for ongoing events
        last_day = now

    top_events = (
        db.session.query(Event)
        .outerjoin(Attendance)
        .filter(Event.start_time >= first_day, Event.start_time <= last_day)
        .group_by(Event.id)
        .order_by(func.count(Attendance.id).desc())
        .limit(5)
        .all()
    )

    return render_template("peak_events.html", top_events=top_events, selected_month=month)


@bp.route("/contact")
def contact():
    return render_template("contact.html")


@bp.route('/download_ics/<int:event_id>')
def download_ics(event_id):
    event = Event.query.get_or_404(event_id)
    ics_content = generate_ics_file(event)

    return Response(
        ics_content,
        mimetype='text/calendar',
        headers={"Content-Disposition": f"attachment; filename={event.title}.ics"}
    )
    

@bp.route('/promote_event/<int:event_id>')
def promote_event(event_id):
    event = Event.query.get_or_404(event_id)
    ca = User.query.filter_by(id=event.host_ca_id).first_or_404()
    mailto_link = generate_promotion_email(event, ca)
        
    return redirect(mailto_link)


@bp.route('/refer_friend/<int:event_id>')
def refer_friend(event_id):
    event = Event.query.get_or_404(event_id)
    mailto_link = generate_forward_to_friend_email(event)
        
    return redirect(mailto_link)


@bp.route('/contact_ca/<int:event_id>')
def contact_ca(event_id):
    event = Event.query.get_or_404(event_id)
    ca = User.query.filter_by(id=event.host_ca_id).first_or_404()
    mailto_link = generate_message_to_ca(ca, event)

    return redirect(mailto_link)


@bp.route("/event/<int:event_id>/checkin", methods=["GET", "POST"])
def checkin(event_id):
    event = Event.query.get_or_404(event_id)

    if datetime.now(pytz.UTC)  > change_timezome(event.end_time) + timedelta(hours=1):
        flash("Check-in is closed for this event.", "danger")
        return redirect(url_for("main.checkin_closed", event_id=event_id))

    if request.method == "POST":
        email = request.form.get("email").strip().lower()

        # Check duplicate entry
        existing = Attendance.query.filter_by(event_id=event_id, user_email=email).first()
        if existing:
            flash("You have already checked in for this event.", "warning")
            return redirect(url_for("main.checkin", event_id=event_id))

        # Save attendance
        new_attendance = Attendance(event_id=event_id, user_email=email)
        db.session.add(new_attendance)
        db.session.commit()

        flash("Attendance recorded! Thank you.", "success")
        return redirect(url_for("main.checkin_success"))

    return render_template("events/checkin.html", event=event)


@bp.route("/event/checkin_closed")
def checkin_closed():
    return render_template("events/checkin_closed.html")


@bp.route("/checkin-success")
def checkin_success():
    return render_template("events/checkin_success.html")


@bp.route("/ca/event/<int:event_id>/past")
@login_required
@ca_required
def past_event_detail(event_id):
    event = Event.query.get_or_404(event_id)

    # Ensure only the host CA can view
    if current_user.id != event.host_ca_id and current_user.id != (event.collab_ca_id or -1): 
        abort(403)

    # Ensure this is truly a past event
    if change_timezome(event.start_time) > datetime.now(pytz.UTC):
        return redirect(url_for("main.your_event_detail", event_id=event.id))

    return render_template("ca/your_past_event_detail.html", event=event)

