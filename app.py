from flask import Flask, request, jsonify, abort, render_template
from flask_cors import CORS

from models import setup_db, db

app = Flask(__name__)
setup_db(app)
CORS(app)
db.create_all()


@app.route("/")
def get_meeting():
    return render_template("index.html")
