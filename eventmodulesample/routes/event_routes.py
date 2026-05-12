

from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models.event import Event, Attendance
 
event_bp = Blueprint('event_bp', __name__)
 
 
# ── VIEW ALL EVENTS ──────────────────────────────────────────────
@event_bp.route('/')
@event_bp.route('/events')
def events():
    all_events = Event.query.order_by(Event.event_date.asc()).all()
    return render_template('events/events.html', events=all_events)
 
 
# ── VIEW SINGLE EVENT ────────────────────────────────────────────
@event_bp.route('/events/<int:event_id>')
def view_event(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('events/view_event.html', event=event)
 
 
# ── CREATE EVENT ─────────────────────────────────────────────────
@event_bp.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        form = request.form
 
        # --- Server-side required field check ---
        required_fields = ['event_name', 'event_type', 'status', 'event_date', 'start_time', 'end_time']
        for field in required_fields:
            if not form.get(field, '').strip():
                flash(f'"{field.replace("_", " ").title()}" is required.', 'danger')
                return render_template('events/create_event.html', form_data=form)
 
        event_name = form['event_name'].strip()
        event_date = form['event_date'].strip()
        start_time = form['start_time'].strip()
        end_time   = form['end_time'].strip()
 
        # --- Duplicate check: same name + same date ---
        duplicate = Event.query.filter(
            db.func.lower(Event.event_name) == event_name.lower(),
            Event.event_date == event_date
        ).first()
 
        if duplicate:
            flash(
                f'An event named "{event_name}" already exists on {event_date}. '
                'Please use a different name or date.',
                'danger'
            )
            return render_template('events/create_event.html', form_data=form)
 
        # --- Time order check ---
        if end_time <= start_time:
            flash('End time must be after start time.', 'danger')
            return render_template('events/create_event.html', form_data=form)
 
        # --- Attendance check ---
        attendance_raw = form.get('expected_attendance', '').strip()
        attendance = None
        if attendance_raw:
            try:
                attendance = int(attendance_raw)
                if attendance < 1:
                    raise ValueError
            except ValueError:
                flash('Expected attendance must be a positive number.', 'danger')
                return render_template('events/create_event.html', form_data=form)
 
        new_event = Event(
            event_name=event_name,
            event_type=form['event_type'],
            description=form.get('description', '').strip() or None,
            location=form.get('location', '').strip() or None,
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            expected_attendance=attendance,
            status=form['status']
        )
 
        db.session.add(new_event)
        db.session.commit()
 
        flash(f'Event "{new_event.event_name}" was created successfully.', 'success')
        return redirect(url_for('event_bp.events'))
 
    return render_template('events/create_event.html', form_data=None)
 
 
# ── EDIT EVENT ───────────────────────────────────────────────────
@event_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
 
    if request.method == 'POST':
        form = request.form
 
        # --- Server-side required field check ---
        required_fields = ['event_name', 'event_type', 'status', 'event_date', 'start_time', 'end_time']
        for field in required_fields:
            if not form.get(field, '').strip():
                flash(f'"{field.replace("_", " ").title()}" is required.', 'danger')
                return render_template('events/edit_event.html', event=event)
 
        event_name = form['event_name'].strip()
        event_date = form['event_date'].strip()
        start_time = form['start_time'].strip()
        end_time   = form['end_time'].strip()
 
        # --- Duplicate check (exclude self) ---
        duplicate = Event.query.filter(
            db.func.lower(Event.event_name) == event_name.lower(),
            Event.event_date == event_date,
            Event.event_id != event_id
        ).first()
 
        if duplicate:
            flash(
                f'Another event named "{event_name}" already exists on {event_date}.',
                'danger'
            )
            return render_template('events/edit_event.html', event=event)
 
        # --- Time order check ---
        if end_time <= start_time:
            flash('End time must be after start time.', 'danger')
            return render_template('events/edit_event.html', event=event)
 
        # --- Attendance check ---
        attendance_raw = form.get('expected_attendance', '').strip()
        attendance = None
        if attendance_raw:
            try:
                attendance = int(attendance_raw)
                if attendance < 1:
                    raise ValueError
            except ValueError:
                flash('Expected attendance must be a positive number.', 'danger')
                return render_template('events/edit_event.html', event=event)
 
        event.event_name         = event_name
        event.event_type         = form['event_type']
        event.description        = form.get('description', '').strip() or None
        event.location           = form.get('location', '').strip() or None
        event.event_date         = event_date
        event.start_time         = start_time
        event.end_time           = end_time
        event.expected_attendance = attendance
        event.status             = form['status']
 
        db.session.commit()
 
        flash(f'Event "{event.event_name}" was updated successfully.', 'success')
        return redirect(url_for('event_bp.view_event', event_id=event.event_id))
 
    return render_template('events/edit_event.html', event=event)
 
 
# ── DELETE EVENT ─────────────────────────────────────────────────
@event_bp.route('/events/<int:event_id>/delete', methods=['POST'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    name = event.event_name
 
    # Remove attendance records first to satisfy the FK constraint
    # (handles existing DB rows that pre-date the cascade definition)
    Attendance.query.filter_by(event_id=event_id).delete()
 
    db.session.delete(event)
    db.session.commit()
    flash(f'Event "{name}" was deleted.', 'success')
    return redirect(url_for('event_bp.events'))