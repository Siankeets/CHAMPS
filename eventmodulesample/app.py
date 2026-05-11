from flask import Flask
from config import Config
from extensions import db

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

# Import routes AFTER app creation
from routes.event_routes import event_bp

app.register_blueprint(event_bp)

if __name__ == '__main__':
    
    with app.app_context():
        db.create_all()

    app.run(debug=True)