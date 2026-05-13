from flask import Flask
from config import Config
from extensions import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

@app.route("/")
def home():
    return "Admin View Eligibles Running"

if __name__ == "__main__":
    app.run(debug=True, port=5001)