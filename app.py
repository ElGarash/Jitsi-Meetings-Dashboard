from datetime import datetime

from flask import Flask, request, jsonify, abort, render_template, Response
from flask_cors import CORS
from flask_migrate import Migrate

from models import setup_db, db, Participant, Meeting, Label

app = Flask(__name__)
setup_db(app)
migrate = Migrate(app, db)
CORS(app)


# Request CORS Headers
@app.after_request
def after_request(response):
    allowed_headers = "Content-Type,Authorization,true"
    response.headers.add("Access-Control-Allow-Headers", allowed_headers)
    allowed_methods = "GET,PUT,POST,DELETE,OPTIONS"
    response.headers.add("Access-Control-Allow-Methods", allowed_methods)
    return response


@app.route("/")
def render_meeting():
    return render_template("index.html")


@app.route("/dashboard")
def get_dashboard():
    page = request.args.get("page", 1)
    limit = request.args.get("limit", 10)
    meetings = Meeting.query.paginate(page, limit, False).items
    return jsonify({"meetings": [meeting.format() for meeting in meetings]})


@app.route("/dashboard", methods=["POST"])
def get_participants_info():
    request_body = request.json
    meeting_date = datetime.now()
    Meeting(date=meeting_date).insert()
    participants = request_body.get("participants", None)
    for participant in participants:
        Participant(name=participant, meeting_date=meeting_date).insert()
    return Response(status=201)
