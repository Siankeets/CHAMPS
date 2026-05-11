from flask import Blueprint, render_template, request, redirect
from extensions import db
from models.event import Event

event_bp = Blueprint('event_bp', __name__)

# VIEW EVENTS
@event_bp.route('/')
@event_bp.route('/events')
def events():

    all_events = Event.query.all()

    return render_template(
        'events/events.html',
        events=all_events
    )


# CREATE EVENT
@event_bp.route('/create_event', methods=['GET', 'POST'])
def create_event():

    if request.method == 'POST':

        new_event = Event(
            event_name=request.form['event_name'],
            event_type=request.form['event_type'],
            description=request.form['description'],
            location=request.form['location'],
            event_date=request.form['event_date'],
            start_time=request.form['start_time'],
            end_time=request.form['end_time'],
            expected_attendance=request.form['expected_attendance'],
            status=request.form['status']
        )

        db.session.add(new_event)

        db.session.commit()

        return redirect('/events')

    return render_template('events/create_event.html')