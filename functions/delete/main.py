import os
import azure.functions as func
from datetime import datetime
from github import Github

from ..models import session, Meeting, Label, Participant, session
from ..auth import get_token_from_auth_header, verify_decode_jwt, check_permissions, PERMISSION
from ..github import clone_db_file, push_db_file

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Authentication and Authorization.
    token, token_err = get_token_from_auth_header(req)
    if token_err:
        return func.HttpResponse(token_err.message, status_code=token_err.status_code)
    payload, payload_err = verify_decode_jwt(token)
    if payload_err:
        return func.HttpResponse(payload_err.message, status_code=payload_err.status_code)
    permissions_err = check_permissions(PERMISSION, payload)
    if permissions_err:
        return func.HttpResponse(permissions_err.message, status_code=permissions_err.status_code)
    # Clone the database, delete the specified meeting, then push it.
    db_file_metadata = clone_db_file()
    deletion_error = delete_meeting(req.params.get("id"))
    if deletion_error:
        return func.HttpResponse(deletion_error['message'], status_code=deletion_error['status_code'])
    push_db_file(db_file_metadata)
    
    return func.HttpResponse("Successfully deleted the meeting", status_code=200)


def delete_meeting(meeting_id):
    meeting = session.get(Meeting, meeting_id)
    if meeting is None:
        return {"message": "Meeting doesn't exist", "status_code": 404}
    else:
        meeting.delete()
