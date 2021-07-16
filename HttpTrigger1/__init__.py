import logging
import azure.functions as func
from datetime import datetime

from .models import Label, Participant, Meeting, create_tables


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")
    request_body = req.get_json()
    insert_into_db(request_body)
    return func.HttpResponse(
        "Items successfully added to the database", status_code=201
    )


def insert_into_db(data):
    create_tables()
    meeting_date = datetime.now()
    Meeting(date=meeting_date).insert()
    participants = data.get("participants", [])
    labels = data.get("labels", [])
    for participant in participants:
        Participant(name=participant, meeting_date=meeting_date).insert()
    for label in labels:
        Label(name=label, meeting_date=meeting_date).insert()
