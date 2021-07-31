import os
import logging
from typing import Union
import azure.functions as func
from datetime import datetime
from github import Github
from sqlalchemy.exc import SQLAlchemyError


from ..models import Label, Participant, Meeting, create_tables, database_location
from ..auth import get_token_from_auth_header, verify_decode_jwt, check_permissions, PERMISSION

ACCESS_TOKEN = os.environ["GITHUB_ACCESS_TOKEN"]
REPO_FULL_NAME = "ElGarash/Jitsi-Meetings-Dashboard"
TARGET_BRANCH = "gh-pages"
DATE_FORMAT = "%B %d, %Y - %I:%M %p"


def main(req: func.HttpRequest) -> func.HttpResponse:
    token, token_err = get_token_from_auth_header(req)
    if token_err:
        return func.HttpResponse(token_err.message, status_code=token_err.status_code)
    payload, payload_err = verify_decode_jwt(token)
    if payload_err:
        return func.HttpResponse(payload_err.message, status_code=payload_err.status_code)
    permissions_err = check_permissions(PERMISSION, payload)
    if permissions_err:
        return func.HttpResponse(permissions_err.message, status_code=permissions_err.status_code)

    g = Github(ACCESS_TOKEN)
    repo = g.get_repo(REPO_FULL_NAME)
    db_file_contents = repo.get_contents("database.db", ref=TARGET_BRANCH)
    with open(database_location, "wb") as db_file:
        db_file.write(db_file_contents.decoded_content)

    request_body = req.get_json()
    insertion_error = insert_into_db(request_body)
    if insertion_error:
        return func.HttpResponse(insertion_error["message"], status_code=insertion_error["status_code"])

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


def insert_into_db(data) -> Union[dict, None]:
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
    participants = data.get("participants", [])
    labels = data.get("labels", [])
    try:
        for participant in participants:
            Participant(participant, meeting_date).insert()
        for label in labels:
            Label(label, meeting_date).insert()
    except SQLAlchemyError:
        return {
            "message": "Failed to insert data into the database.",
            "status_code": 422,
        }
