from extensions import db

class Event(db.Model):

    __tablename__ = 'events'

    event_id = db.Column(db.Integer, primary_key=True)

    event_name = db.Column(db.String(255), nullable=False)

    event_type = db.Column(db.String(100), nullable=False)

    description = db.Column(db.Text)

    location = db.Column(db.String(255))

    event_date = db.Column(db.Date)

    start_time = db.Column(db.Time)

    end_time = db.Column(db.Time)

    expected_attendance = db.Column(db.Integer)

    status = db.Column(db.String(50))