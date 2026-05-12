import datetime
from flask import Flask
from config import Config
from extensions import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


# ── Safe date filter ──────────────────────────────────────────────
@app.template_filter('safe_date')
def safe_date(value, fmt='%b %d, %Y'):
    if not value:
        return '—'
    try:
        return value.strftime(fmt)
    except (ValueError, AttributeError):
        return '—'


# ── Safe time filter ──────────────────────────────────────────────
# PyMySQL returns MariaDB TIME columns as datetime.timedelta, not datetime.time.
# This filter handles both so strftime works correctly.
@app.template_filter('safe_time')
def safe_time(value, fmt='%I:%M %p'):
    if value is None:
        return '—'
    if isinstance(value, datetime.timedelta):
        total = int(value.total_seconds())
        h, rem = divmod(total, 3600)
        m = rem // 60
        try:
            value = datetime.time(hour=h % 24, minute=m)
        except ValueError:
            return '—'
    try:
        return value.strftime(fmt)
    except (ValueError, AttributeError):
        return '—'


# ── HH:MM filter for <input type="time"> value= attributes ───────
@app.template_filter('to_hhmm')
def to_hhmm(value):
    if value is None:
        return ''
    if isinstance(value, datetime.timedelta):
        total = int(value.total_seconds())
        h, rem = divmod(total, 3600)
        m = rem // 60
        return f'{h % 24:02d}:{m:02d}'
    try:
        return value.strftime('%H:%M')
    except (ValueError, AttributeError):
        return ''


from routes.event_routes import event_bp
app.register_blueprint(event_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)