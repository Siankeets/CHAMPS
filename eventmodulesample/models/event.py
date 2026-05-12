from extensions import db
from datetime import datetime
 
 
class Member(db.Model):
    __tablename__ = 'members'
 
    member_id  = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name  = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(255), nullable=True)
    phone      = db.Column(db.String(30),  nullable=True)
    role       = db.Column(db.String(100), nullable=True)
    position   = db.Column(db.String(100), nullable=True)
    status     = db.Column(db.String(50),  nullable=False, default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
 
    attendances = db.relationship('Attendance', backref='member', lazy=True)
 
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
 
 
class Attendance(db.Model):
    __tablename__ = 'attendance'
 
    attendance_id     = db.Column(db.Integer, primary_key=True)
    event_id          = db.Column(db.Integer, db.ForeignKey('events.event_id',   ondelete='CASCADE'),  nullable=False)
    member_id         = db.Column(db.Integer, db.ForeignKey('members.member_id', ondelete='SET NULL'), nullable=True)
    attendance_status = db.Column(db.String(50), nullable=False, default='Present')
    check_in_time     = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
 
 
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
 
    attendances = db.relationship(
        'Attendance',
        backref='event',
        lazy=True,
        cascade='all, delete-orphan',
        passive_deletes=True
    )