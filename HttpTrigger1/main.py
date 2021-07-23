import os
import logging
import azure.functions as func
from datetime import datetime
from github import Github


from .models import Label, Participant, Meeting, create_tables, database_location
from .auth import *

ACCESS_TOKEN = os.environ["GITHUB_ACCESS_TOKEN"]
REPO_FULL_NAME = "ElGarash/Jitsi-Meetings-Dashboard"
TARGET_BRANCH = "gh-pages"


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        token = get_token_auth_header(req)
        payload = verify_decode_jwt(token)
        check_permissions(PERMISSION, payload)
    except AuthError as e:
        return func.HttpResponse(f"{e.message}", status_code=e.status_code)

    g = Github(ACCESS_TOKEN)
    repo = g.get_repo(REPO_FULL_NAME)
    db_file_contents = repo.get_contents("database.db", ref=TARGET_BRANCH)
    with open(database_location, "wb") as db_file:
        db_file.write(db_file_contents.decoded_content)

    request_body = req.get_json()
    insert_into_db(request_body)

    with open(database_location, "rb") as db_file:
        updated_content = db_file.read()

    repo.update_file(
        path=db_file_contents.path,
        message=f'Azure: "{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}"',
        content=updated_content,
        sha=db_file_contents.sha,
        branch=TARGET_BRANCH,
    )
    
    return func.HttpResponse("Successful operation", status_code=200)


def insert_into_db(data):
    create_tables()  # Create the tables if not already created.
    meeting_date = datetime.now()
    Meeting(date=meeting_date).insert()
    participants = data.get("participants", [])
    labels = data.get("labels", [])
    for participant in participants:
        Participant(name=participant, meeting_date=meeting_date).insert()
    for label in labels:
        Label(name=label, meeting_date=meeting_date).insert()
