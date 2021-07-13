from datetime import datetime

from flask import Flask, request, jsonify, abort, render_template
from flask_cors import CORS
from flask_migrate import Migrate

from models import setup_db, db, Participant, Meeting, Label

app = Flask(__name__)
setup_db(app)
CORS(app)
migrate = Migrate(app, db)


@app.route("/")
def render_meeting():
    return render_template("index.html")


@app.route("/dashboard", methods=["POST"])
def get_participants_info():
    request_body = request.json
    meeting_date = datetime.now()
    Meeting(date=meeting_date).insert()
    participants = request_body.get("participants", None)
    for participant in participants:
        Participant(name=participant, meeting_date=meeting_date).insert()
    return None
