
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database config (SQLite file in same folder)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Example Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Make sure tables are created once when app starts
def create_tables():
    with app.app_context():
        db.create_all()

create_tables()   # call once at startup

@app.route("/")
def home():
    return "Flask app with DB is running fine ✅"

if __name__ == "__main__":
    app.run(debug=True)
