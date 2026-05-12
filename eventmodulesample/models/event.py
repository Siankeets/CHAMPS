from extensions import db
from datetime import datetime
 
 
class Attendance(db.Model):
    """Mirrors the attendance table. Cascade delete keeps FK constraint happy."""
    __tablename__ = 'attendance'
 
    attendance_id     = db.Column(db.Integer, primary_key=True)
    event_id          = db.Column(db.Integer, db.ForeignKey('events.event_id', ondelete='CASCADE'))
    member_id         = db.Column(db.Integer)
    attendance_status = db.Column(db.String(50))
    check_in_time     = db.Column(db.DateTime, default=datetime.utcnow)
 
 
class Event(db.Model):
    __tablename__ = 'events'
 
    event_id            = db.Column(db.Integer, primary_key=True)
    event_name          = db.Column(db.String(255), nullable=False)
    event_type          = db.Column(db.String(100), nullable=False)
    description         = db.Column(db.Text)
    location            = db.Column(db.String(255))
    event_date          = db.Column(db.Date)
    start_time          = db.Column(db.Time)
    end_time            = db.Column(db.Time)
    expected_attendance = db.Column(db.Integer)
    status              = db.Column(db.String(50))
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)
 
    # Cascade: deleting an Event also deletes its Attendance rows first
    attendances = db.relationship(
        'Attendance',
        backref='event',
        lazy=True,
        cascade='all, delete-orphan',
        passive_deletes=True
    )