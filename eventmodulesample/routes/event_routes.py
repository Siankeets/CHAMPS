from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models.event import Event, Attendance, Member
from datetime import datetime

event_bp = Blueprint('event_bp', __name__)


# ── VIEW ALL EVENTS ──────────────────────────────────────────────
@event_bp.route('/')
@event_bp.route('/events')
def events():
    all_events = Event.query.order_by(Event.event_date.asc()).all()
    return render_template('events/events.html', events=all_events, active_page='events')


# ── VIEW SINGLE EVENT ────────────────────────────────────────────
@event_bp.route('/events/<int:event_id>')
def view_event(event_id):
    event = Event.query.get_or_404(event_id)
    attendances   = Attendance.query.filter_by(event_id=event_id).all()
    present_count = sum(1 for a in attendances if a.attendance_status == 'Present')
    late_count    = sum(1 for a in attendances if a.attendance_status == 'Late')
    absent_count  = sum(1 for a in attendances if a.attendance_status == 'Absent')
    return render_template(
        'events/view_event.html',
        event=event,
        attendances=attendances,
        present_count=present_count,
        late_count=late_count,
        absent_count=absent_count,
        active_page='events',
    )


# ── CREATE EVENT ─────────────────────────────────────────────────
@event_bp.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        form = request.form

        required_fields = ['event_name', 'event_type', 'status', 'event_date', 'start_time', 'end_time']
        for field in required_fields:
            if not form.get(field, '').strip():
                flash(f'"{field.replace("_", " ").title()}" is required.', 'danger')
                return render_template('events/create_event.html', form_data=form, active_page='events')

        event_name = form['event_name'].strip()
        event_date = form['event_date'].strip()
        start_time = form['start_time'].strip()
        end_time   = form['end_time'].strip()

        duplicate = Event.query.filter(
            db.func.lower(Event.event_name) == event_name.lower(),
            Event.event_date == event_date
        ).first()
        if duplicate:
            flash(f'An event named "{event_name}" already exists on {event_date}.', 'danger')
            return render_template('events/create_event.html', form_data=form, active_page='events')

        if end_time <= start_time:
            flash('End time must be after start time.', 'danger')
            return render_template('events/create_event.html', form_data=form, active_page='events')

        attendance_raw = form.get('expected_attendance', '').strip()
        attendance = None
        if attendance_raw:
            try:
                attendance = int(attendance_raw)
                if attendance < 1:
                    raise ValueError
            except ValueError:
                flash('Expected attendance must be a positive number.', 'danger')
                return render_template('events/create_event.html', form_data=form, active_page='events')

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

    return render_template('events/create_event.html', form_data=None, active_page='events')


# ── EDIT EVENT ───────────────────────────────────────────────────
@event_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        form = request.form

        required_fields = ['event_name', 'event_type', 'status', 'event_date', 'start_time', 'end_time']
        for field in required_fields:
            if not form.get(field, '').strip():
                flash(f'"{field.replace("_", " ").title()}" is required.', 'danger')
                return render_template('events/edit_event.html', event=event, active_page='events')

        event_name = form['event_name'].strip()
        event_date = form['event_date'].strip()
        start_time = form['start_time'].strip()
        end_time   = form['end_time'].strip()

        duplicate = Event.query.filter(
            db.func.lower(Event.event_name) == event_name.lower(),
            Event.event_date == event_date,
            Event.event_id != event_id
        ).first()
        if duplicate:
            flash(f'Another event named "{event_name}" already exists on {event_date}.', 'danger')
            return render_template('events/edit_event.html', event=event, active_page='events')

        if end_time <= start_time:
            flash('End time must be after start time.', 'danger')
            return render_template('events/edit_event.html', event=event, active_page='events')

        attendance_raw = form.get('expected_attendance', '').strip()
        attendance = None
        if attendance_raw:
            try:
                attendance = int(attendance_raw)
                if attendance < 1:
                    raise ValueError
            except ValueError:
                flash('Expected attendance must be a positive number.', 'danger')
                return render_template('events/edit_event.html', event=event, active_page='events')

        event.event_name          = event_name
        event.event_type          = form['event_type']
        event.description         = form.get('description', '').strip() or None
        event.location            = form.get('location', '').strip() or None
        event.event_date          = event_date
        event.start_time          = start_time
        event.end_time            = end_time
        event.expected_attendance = attendance
        event.status              = form['status']

        db.session.commit()
        flash(f'Event "{event.event_name}" was updated successfully.', 'success')
        return redirect(url_for('event_bp.view_event', event_id=event.event_id))

    return render_template('events/edit_event.html', event=event, active_page='events')


# ── DELETE EVENT ─────────────────────────────────────────────────
@event_bp.route('/events/<int:event_id>/delete', methods=['POST'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    name = event.event_name
    Attendance.query.filter_by(event_id=event_id).delete()
    db.session.delete(event)
    db.session.commit()
    flash(f'Event "{name}" was deleted.', 'success')
    return redirect(url_for('event_bp.events'))


# ── ATTENDANCE: ALL EVENTS VIEW ───────────────────────────────────
@event_bp.route('/attendance')
def attendance_home():
    all_events = Event.query.order_by(Event.event_date.desc()).all()
    event_stats = []
    for ev in all_events:
        recs = Attendance.query.filter_by(event_id=ev.event_id).all()
        event_stats.append({
            'event':   ev,
            'total':   len(recs),
            'present': sum(1 for r in recs if r.attendance_status == 'Present'),
            'late':    sum(1 for r in recs if r.attendance_status == 'Late'),
            'absent':  sum(1 for r in recs if r.attendance_status == 'Absent'),
        })

    # Build ARIMA forecasts — fails silently if statsmodels not installed
    try:
        from utils.forecasting import build_forecasts
        forecasts = build_forecasts(event_stats)
    except Exception:
        forecasts = []

    return render_template(
        'events/attendance_home.html',
        event_stats=event_stats,
        forecasts=forecasts,
        active_page='attendance',
    )


# ── REPORTS ───────────────────────────────────────────────────────
@event_bp.route('/reports')
def reports():
    all_events = Event.query.order_by(Event.event_date.asc()).all()
    event_stats = []
    for ev in all_events:
        recs = Attendance.query.filter_by(event_id=ev.event_id).all()
        event_stats.append({
            'event':   ev,
            'total':   len(recs),
            'present': sum(1 for r in recs if r.attendance_status == 'Present'),
            'late':    sum(1 for r in recs if r.attendance_status == 'Late'),
            'absent':  sum(1 for r in recs if r.attendance_status == 'Absent'),
        })

    try:
        from utils.forecasting import build_forecasts
        forecasts = build_forecasts(event_stats)
    except Exception:
        forecasts = []

    return render_template(
        'events/reports.html',
        event_stats=event_stats,
        forecasts=forecasts,
        active_page='reports',
    )


# ── ATTENDANCE: PER EVENT ─────────────────────────────────────────
@event_bp.route('/attendance/<int:event_id>', methods=['GET', 'POST'])
def attendance_event(event_id):
    event   = Event.query.get_or_404(event_id)
    members = Member.query.filter_by(status='Active').order_by(Member.last_name.asc()).all()

    if request.method == 'POST':
        action = request.form.get('action')

        # --- Add single member to attendance ---
        if action == 'add':
            member_id = request.form.get('member_id', '').strip()
            status    = request.form.get('attendance_status', 'Present').strip()

            if not member_id:
                flash('Please select a member.', 'danger')
                return redirect(url_for('event_bp.attendance_event', event_id=event_id))

            if status not in ('Present', 'Absent', 'Late'):
                flash('Invalid attendance status.', 'danger')
                return redirect(url_for('event_bp.attendance_event', event_id=event_id))

            existing = Attendance.query.filter_by(event_id=event_id, member_id=member_id).first()
            if existing:
                flash('This member is already recorded for this event.', 'warning')
                return redirect(url_for('event_bp.attendance_event', event_id=event_id))

            record = Attendance(
                event_id=event_id,
                member_id=int(member_id),
                attendance_status=status,
                check_in_time=datetime.utcnow()
            )
            db.session.add(record)
            db.session.commit()
            member = Member.query.get(member_id)
            flash(f'"{member.full_name}" added as {status}.', 'success')

        # --- Bulk add multiple members ---
        elif action == 'add_bulk':
            member_ids  = request.form.getlist('member_ids')
            bulk_status = request.form.get('bulk_status', 'Present').strip()

            if not member_ids:
                flash('No members selected for bulk add.', 'danger')
                return redirect(url_for('event_bp.attendance_event', event_id=event_id))

            if bulk_status not in ('Present', 'Absent', 'Late'):
                bulk_status = 'Present'

            # Get already-recorded IDs to skip duplicates
            already = {
                r.member_id
                for r in Attendance.query.filter_by(event_id=event_id).all()
            }

            added = 0
            skipped = 0
            for mid in member_ids:
                try:
                    mid_int = int(mid)
                except ValueError:
                    continue
                if mid_int in already:
                    skipped += 1
                    continue
                db.session.add(Attendance(
                    event_id=event_id,
                    member_id=mid_int,
                    attendance_status=bulk_status,
                    check_in_time=datetime.utcnow()
                ))
                added += 1

            db.session.commit()

            if added:
                msg = f'{added} member{"s" if added != 1 else ""} added as {bulk_status}.'
                if skipped:
                    msg += f' ({skipped} already recorded, skipped.)'
                flash(msg, 'success')
            else:
                flash('All selected members were already recorded for this event.', 'warning')

        # --- Update status inline ---
        elif action == 'update_status':
            attendance_id = request.form.get('attendance_id')
            new_status    = request.form.get('attendance_status', '').strip()
            record = Attendance.query.get_or_404(attendance_id)
            if record.event_id != event_id:
                flash('Invalid operation.', 'danger')
                return redirect(url_for('event_bp.attendance_event', event_id=event_id))
            if new_status not in ('Present', 'Absent', 'Late'):
                flash('Invalid status.', 'danger')
                return redirect(url_for('event_bp.attendance_event', event_id=event_id))
            record.attendance_status = new_status
            db.session.commit()
            flash(f'Status updated to {new_status}.', 'success')

        # --- Remove record ---
        elif action == 'delete':
            attendance_id = request.form.get('attendance_id')
            record = Attendance.query.get_or_404(attendance_id)
            if record.event_id != event_id:
                flash('Invalid operation.', 'danger')
                return redirect(url_for('event_bp.attendance_event', event_id=event_id))
            name = record.member.full_name if record.member else 'Unknown'
            db.session.delete(record)
            db.session.commit()
            flash(f'"{name}" removed from attendance.', 'success')

        return redirect(url_for('event_bp.attendance_event', event_id=event_id))

    # GET
    records = (
        Attendance.query
        .filter_by(event_id=event_id)
        .join(Member, Attendance.member_id == Member.member_id)
        .order_by(Member.last_name.asc())
        .all()
    )
    recorded_ids  = {r.member_id for r in records}
    present_count = sum(1 for r in records if r.attendance_status == 'Present')
    late_count    = sum(1 for r in records if r.attendance_status == 'Late')
    absent_count  = sum(1 for r in records if r.attendance_status == 'Absent')

    return render_template(
        'events/attendance_event.html',
        event=event,
        records=records,
        members=members,
        recorded_ids=recorded_ids,
        present_count=present_count,
        late_count=late_count,
        absent_count=absent_count,
        active_page='attendance',
    )


# ── MEMBERS: LIST ─────────────────────────────────────────────────
@event_bp.route('/members')
def members():
    all_members = Member.query.order_by(Member.last_name.asc()).all()
    return render_template('events/members.html', members=all_members, active_page='members')


# ── MEMBERS: CREATE ───────────────────────────────────────────────
@event_bp.route('/members/add', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        form = request.form
        first = form.get('first_name', '').strip()
        last  = form.get('last_name', '').strip()

        if not first or not last:
            flash('First name and last name are required.', 'danger')
            return render_template('events/add_member.html', form_data=form, active_page='members')

        duplicate = Member.query.filter(
            db.func.lower(Member.first_name) == first.lower(),
            db.func.lower(Member.last_name)  == last.lower()
        ).first()
        if duplicate:
            flash(f'A member named "{first} {last}" already exists.', 'warning')
            return render_template('events/add_member.html', form_data=form, active_page='members')

        member = Member(
            first_name = first,
            last_name  = last,
            email      = form.get('email', '').strip() or None,
            phone      = form.get('phone', '').strip() or None,
            role       = form.get('role', '').strip() or None,
            position   = form.get('position', '').strip() or None,
            status     = form.get('status', 'Active'),
        )
        db.session.add(member)
        db.session.commit()
        flash(f'Member "{member.full_name}" added successfully.', 'success')
        return redirect(url_for('event_bp.members'))

    return render_template('events/add_member.html', form_data=None, active_page='members')


# ── MEMBERS: DELETE ───────────────────────────────────────────────
@event_bp.route('/members/<int:member_id>/delete', methods=['POST'])
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    name   = member.full_name
    db.session.delete(member)
    db.session.commit()
    flash(f'Member "{name}" was removed.', 'success')
    return redirect(url_for('event_bp.members'))