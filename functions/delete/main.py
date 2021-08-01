import os
import azure.functions as func
from datetime import datetime
from github import Github

from ..models import session, database_location, Meeting, Label, Participant, session
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
    # Delete a specific meeting from the database.
    meeting_id = req.params.get("id")
    deletion_error = delete_meeting(meeting_id)
    if deletion_error:
        return func.HttpResponse(deletion_error['message'], status_code=deletion_error['status_code'])
    # Read the database after deletion and commit it to GitHub.
    with open(database_location, "rb") as db_file:
        updated_content = db_file.read()
    repo.update_file(
        path=db_file_contents.path,
        message=f"Azure at {datetime.now().strftime(DATE_FORMAT)}",
        content=updated_content,
        sha=db_file_contents.sha,
        branch=TARGET_BRANCH,
    )

    return func.HttpResponse("Successfully deleted the meeting", status_code=200)


def delete_meeting(meeting_id):
    meeting = session.get(Meeting, meeting_id)
    if meeting is None:
        return {"message": "Meeting doesn't exist", "status_code": 404}
    else:
        meeting.delete()
