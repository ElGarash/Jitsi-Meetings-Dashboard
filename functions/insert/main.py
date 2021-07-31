import os
from typing import Union
import azure.functions as func
from datetime import datetime
from github import Github
from sqlalchemy.exc import SQLAlchemyError


from ..models import Label, Participant, Meeting, create_tables, database_location, session
from ..auth import get_token_from_auth_header, verify_decode_jwt, check_permissions, PERMISSION

ACCESS_TOKEN = os.environ["GITHUB_ACCESS_TOKEN"]
REPO_FULL_NAME = "ElGarash/Jitsi-Meetings-Dashboard"
TARGET_BRANCH = "gh-pages"
DATE_FORMAT = "%B %d, %Y - %I:%M %p"


def main(req: func.HttpRequest) -> func.HttpResponse:
    # Authentication and Authorization
    token, token_err = get_token_from_auth_header(req)
    if token_err:
        return func.HttpResponse(token_err.message, status_code=token_err.status_code)
    payload, payload_err = verify_decode_jwt(token)
    if payload_err:
        return func.HttpResponse(payload_err.message, status_code=payload_err.status_code)
    permissions_err = check_permissions(PERMISSION, payload)
    if permissions_err:
        return func.HttpResponse(permissions_err.message, status_code=permissions_err.status_code)
    # Get database file from GitHub
    g = Github(ACCESS_TOKEN)
    repo = g.get_repo(REPO_FULL_NAME)
    db_file_contents = repo.get_contents("database.db", ref=TARGET_BRANCH)
    with open(database_location, "wb") as db_file:
        db_file.write(db_file_contents.decoded_content)
    # Insert request body data into the database.
    request_body = req.get_json()
    insertion_error = insert_into_db(request_body)
    if insertion_error:
        return func.HttpResponse(insertion_error["message"], status_code=insertion_error["status_code"])
    # Read the database after insertion and commit it to GitHub.
    with open(database_location, "rb") as db_file:
        updated_content = db_file.read()
    repo.update_file(
        path=db_file_contents.path,
        message=f"Azure at {datetime.now().strftime(DATE_FORMAT)}",
        content=updated_content,
        sha=db_file_contents.sha,
        branch=TARGET_BRANCH,
    )

    return func.HttpResponse("Successfully inserted the meeting's data.", status_code=201)


def insert_into_db(request_body) -> Union[dict, None]:
    create_tables()  # Create the tables if not already created.
    current_time_str = datetime.now().strftime(DATE_FORMAT)
    meeting_date = datetime.strptime(current_time_str, DATE_FORMAT)
    try:
        Meeting(meeting_date).insert()
    except SQLAlchemyError:
        return {
            "message": "A meeting with the same date and time already exists.",
            "status_code": 409,
        }
    inserted_meeting = session.query(Meeting).filter(Meeting.date == meeting_date).first()
    get_name = lambda model: model.name
    db_participants = set(map(get_name, session.query(Participant).all()))
    db_labels = set(map(get_name, session.query(Label).all()))
    participants = request_body.get("participants", [])
    labels = request_body.get("labels", [])
    try:
        for participant in participants:
            if participant not in db_participants:
                inserted_meeting.add_child(Participant(participant))
            else:
                participant_instance = session.query(Participant).filter(Participant.name == participant).first()
                inserted_meeting.add_child(participant_instance)
        for label in labels:
            if label not in db_labels:
                inserted_meeting.add_child(Label(label))
            else:
                label_instance = session.query(Label).filter(Label.name == label).first()
                inserted_meeting.add_child(label_instance)
    except SQLAlchemyError:
        return {
            "message": "Failed to insert data into the database.",
            "status_code": 422,
        }
