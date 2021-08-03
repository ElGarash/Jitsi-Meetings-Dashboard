from datetime import datetime
from os import getenv
from typing import Union
from json import dumps
from sqlalchemy.exc import SQLAlchemyError
import azure.functions as func

from ..models import Label, Participant, Meeting, create_tables, session
from ..auth import (
    get_token_from_auth_header,
    verify_decode_jwt,
    check_permissions,
    PERMISSION,
)
from ..github import clone_db_file, push_db_file

RESOURCE_TO_MODEL_MAPPER = {
    "meetings": Meeting,
    "participants": Participant,
    "labels": Label,
}


def main(request: func.HttpRequest) -> func.HttpResponse:
    # Authentication and Authorization.
    token, token_err = get_token_from_auth_header(request)
    if token_err:
        return func.HttpResponse(token_err.message, status_code=token_err.status_code)
    payload, payload_err = verify_decode_jwt(token)
    if payload_err:
        return func.HttpResponse(
            payload_err.message, status_code=payload_err.status_code
        )
    permissions_err = check_permissions(PERMISSION, payload)
    if permissions_err:
        return func.HttpResponse(
            permissions_err.message, status_code=permissions_err.status_code
        )
    # Method dispatching.
    if request.method == "DELETE":
        return delete_dispatcher(request)
    elif request.method == "GET":
        return get_dispatcher(request)
    elif request.method == "PATCH":
        return patch_dispatcher(request)
    elif request.method == "POST":
        return post_dispatcher(request)
    else:
        return func.HttpResponse("Method not allowed", status_code=405)


def get_dispatcher(request):
    GET_RESOURCES = ["secrets", "meetings"]
    resource = request.route_params.get("resources")
    if resource not in GET_RESOURCES:
        return func.HttpResponse("Method Not Allowed", status_code=405)
    elif resource == "secrets":
        secret_type = request.params.get("type", None)
        if secret_type is None:
            return func.HttpResponse("Bad Request", status_code=400)
        secret = getenv(secret_type.upper(), None)
        if secret:
            return func.HttpResponse(secret, status_code=200)
        else:
            return func.HttpResponse("Secret not found", status_code=404)
    elif resource == "meetings":
        if request.route_params.get("id", None):
            return func.HttpResponse("Method Not Allowed", status_code=405)
        clone_db_file()
        active_meetings = (
            session.query(Meeting).filter(Meeting.date_ended == None).all()
        )
        active_meetings_dict = {
            meeting.room_name: meeting.id for meeting in active_meetings
        }
        if not active_meetings:
            return func.HttpResponse("There are no active meetings", status_code=404)
        return func.HttpResponse(
            dumps(active_meetings_dict), status_code=200, mimetype="application/json"
        )


def post_dispatcher(request) -> Union[dict, None]:
    db_file_metadata = clone_db_file()
    create_tables()
    resource = request.route_params.get("resources", None)
    if not resource or request.route_params.get("id", None):
        return func.HttpResponse("Bad request", status_code=400)
    request_body = request.get_json()
    model = RESOURCE_TO_MODEL_MAPPER[resource]
    try:
        if model == Meeting:
            post_meeting(request_body, request.method)
        elif model == Participant:
            post_participant(request_body)
        elif model == Label:
            post_label(request_body)
    except SQLAlchemyError as e:
        session.rollback()
        return func.HttpResponse(str(e), status_code=422)
    push_db_file(db_file_metadata)
    return func.HttpResponse("Resource successfully inserted", status_code=201)


def post_meeting(request_body, request_method):
    date_format = "%B %d, %Y - %I:%M %p"
    current_time_str = datetime.now().strftime(date_format)
    meeting_date = datetime.strptime(current_time_str, date_format)
    meeting_name = request_body.get("room_name")
    Meeting(meeting_name, meeting_date).insert()
    inserted_meeting = (
        session.query(Meeting).filter(Meeting.room_name == meeting_name).first()
    )
    add_participants_and_labels_to_meeting(
        inserted_meeting, request_body, request_method
    )


def add_participants_and_labels_to_meeting(
    inserted_meeting, request_body, request_method
):
    db_participants = [
        participant.name.casefold() for participant in session.query(Participant).all()
    ]
    db_labels = [label.name.casefold() for label in session.query(Label).all()]
    if request_method == "PATCH":
        inserted_meeting.participants.clear()
        inserted_meeting.labels.clear()
    for participant in request_body.get("participants", []):
        if participant.casefold() not in db_participants:
            inserted_meeting.add_child(Participant(participant))
        else:
            participant_instance = (
                session.query(Participant)
                .filter(Participant.name == participant)
                .first()
            )
            inserted_meeting.add_child(participant_instance)
    for label in request_body.get("labels", []):
        if label.casefold() not in db_labels:
            inserted_meeting.add_child(Label(label))
        else:
            label_instance = session.query(Label).filter(Label.name == label).first()
            inserted_meeting.add_child(label_instance)


def post_participant(request_body):
    name = request_body.get("name")
    Participant(name).insert()


def post_label(request_body):
    name = request_body.get("name")
    Label(name).insert()


def delete_dispatcher(request) -> Union[dict, None]:
    DELETE_RESOURCES = ["meetings", "labels", "participants"]
    resource = request.route_params.get("resources", None)
    resource_id = request.route_params.get("id", None)
    if resource not in DELETE_RESOURCES or not resource_id:
        return func.HttpResponse("Bad request", status_code=400)
    model = RESOURCE_TO_MODEL_MAPPER[resource]
    db_file_metadata = clone_db_file()
    resource = session.get(model, resource_id)
    if resource is None:
        return func.HttpResponse("Resource doesn't exist", status_code=404)
    resource.delete()
    push_db_file(db_file_metadata)
    return func.HttpResponse("Successfully deleted the resource", status_code=200)


def patch_dispatcher(request) -> Union[dict, None]:
    PATCH_RESOURCES = ["meetings", "labels", "participants"]
    resource = request.route_params.get("resources", None)
    resource_id = request.route_params.get("id", None)
    if resource not in PATCH_RESOURCES or not resource_id:
        return func.HttpResponse("Bad request", status_code=400)
    request_body = request.get_json()
    model = RESOURCE_TO_MODEL_MAPPER[resource]
    db_file_metadata = clone_db_file()
    resource = session.get(model, resource_id)
    if resource is None:
        return func.HttpResponse("Resource doesn't exist", status_code=404)
    try:
        if model == Meeting:
            patch_meeting(resource, request_body, request.method)
        elif model == Participant:
            patch_participant(resource, request_body)
        elif model == Label:
            patch_label(resource, request_body)
    except SQLAlchemyError as e:
        session.rollback()
        return func.HttpResponse(str(e), status_code=422)
    push_db_file(db_file_metadata)
    return func.HttpResponse("Successfully updated the resource", status_code=200)


def patch_label(resource, request_body):
    resource.name = request_body.get("name", resource.name)
    # resource.meetings = request_body.get("meetings", resource.meetings) # Requires changes + not sure if needed
    resource.update()


def patch_meeting(resource, request_body, request_method):
    resource.room_name = request_body.get("room_name", resource.room_name)
    resource.link = request_body.get("link", resource.link)
    # resource.date_started = request_body.get("date_started", resource.date_started) # Requires changes + not sure if needed
    if request_body.get("ending_flag", None):
        date_format = "%B %d, %Y - %I:%M %p"
        current_time_str = datetime.now().strftime(date_format)
        date_ended = datetime.strptime(current_time_str, date_format)
        resource.date_ended = date_ended
    add_participants_and_labels_to_meeting(resource, request_body, request_method)
    resource.update()


def patch_participant(resource, request_body):
    resource.name = request_body.get("name", resource.name)
    # resource.meetings = request_body.get("meetings", resource.meetings) # Requires changes + not sure if needed
    resource.update()
