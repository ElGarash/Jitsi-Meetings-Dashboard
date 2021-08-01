from datetime import datetime
from os import getenv
from typing import Union
from json import dumps
from sqlalchemy.exc import SQLAlchemyError
import azure.functions as func

from ..models import Label, Participant, Meeting, create_tables, session
from ..auth import get_token_from_auth_header, verify_decode_jwt, check_permissions, PERMISSION
from ..github import clone_db_file, push_db_file

RESOURCE_TO_MODEL_MAPPER = {"meetings": Meeting, "participants": Participant, "labels": Label}

def main(request: func.HttpRequest) -> func.HttpResponse:
    # Authentication and Authorization.
    token, token_err = get_token_from_auth_header(request)
    if token_err:
        return func.HttpResponse(token_err.message, status_code=token_err.status_code)
    payload, payload_err = verify_decode_jwt(token)
    if payload_err:
        return func.HttpResponse(payload_err.message, status_code=payload_err.status_code)
    permissions_err = check_permissions(PERMISSION, payload)
    if permissions_err:
        return func.HttpResponse(permissions_err.message, status_code=permissions_err.status_code)
    # Method dispatching.
    if request.method == 'DELETE':
        resource = request.route_params.get("resources")
        resource_id = request.route_params.get("id")
        db_file_metadata = clone_db_file()
        deletion_error = delete(resource, resource_id)
        if deletion_error:
            return func.HttpResponse(deletion_error['message'], status_code=deletion_error['status_code'])
        push_db_file(db_file_metadata)
        return func.HttpResponse("Successfully deleted the resource", status_code=200)
    
    elif request.method == 'GET':
        resource = request.route_params.get("resources")
        if resource != 'secrets':
            return func.HttpResponse("Method Not Allowed", status_code=405)
        else:
            secret_type = request.params.get("type", None)
            if secret_type is None:
                return func.HttpResponse("Bad Request", status_code=400)
            secret = getenv(secret_type.upper(), None)
            if secret:
                return func.HttpResponse(secret, status_code=200)
            else:
                return func.HttpResponse("Secret not found", status_code=404)
            
        
    elif request.method == 'PATCH':
        resource = request.route_params.get("resources")
        resource_id = request.route_params.get("id")
        request_body = request.get_json()
        db_file_metadata = clone_db_file()
        update_error = update(resource, resource_id, request_body)
        if update_error:
            return func.HttpResponse(update_error["message"], status_code=update_error["status_code"])
        push_db_file(db_file_metadata)
        return func.HttpResponse("Successfully updated the resource", status_code=200)
    elif request.method == 'POST': 
        db_file_metadata = clone_db_file()
        insertion_error = insert(request.get_json())
        if insertion_error:
            return func.HttpResponse(insertion_error["message"], status_code=insertion_error["status_code"])
        push_db_file(db_file_metadata)
        return func.HttpResponse("Successfully inserted the meeting's data", status_code=201)
    
    else:
        return func.HttpResponse("Method not allowed", status_code=405)
    
    

def insert(request_body) -> Union[dict, None]:
    create_tables()
    date_format = "%B %d, %Y - %I:%M %p"
    current_time_str = datetime.now().strftime(date_format)
    meeting_date = datetime.strptime(current_time_str, date_format)
    try:
        Meeting(meeting_date).insert()
    except SQLAlchemyError:
        return {"message": "A meeting with the same date and time already exists", "status_code": 409}
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
        return {"message": "Failed to insert data into the database", "status_code": 422}


def delete(resource, resource_id) -> Union[dict, None]:
    model = RESOURCE_TO_MODEL_MAPPER[resource]
    resource = session.get(model, resource_id)
    if resource is None:
        return {"message": "Resource doesn't exist", "status_code": 404}
    resource.delete()
        
        
def update(resource, resource_id, request_body) -> Union[dict, None]:
    model = RESOURCE_TO_MODEL_MAPPER[resource]
    resource = session.get(model, resource_id)
    if resource is None:
        return {"message": "Resource doesn't exist", "status_code": 404}
    try:
        if model == Meeting:
            resource.date = request_body.get("date", resource.date)
            resource.link = request_body.get("link", resource.link)
            resource.participants = request_body.get("participants", resource.participants)
            resource.labels = request_body.get("labels", resource.labels)
            resource.update()
        elif model == Participant:
            resource.name = request_body.get("name", resource.name)
            resource.meetings = request_body.get("meetings", resource.meetings)
            resource.update()
        elif model == Label:
            resource.name = request_body.get("name", resource.name)
            resource.meetings = request_body.get("meetings", resource.meetings)
            resource.update()
    except SQLAlchemyError:
        return {"message": "Failed to update the resource due to invalid data format", "status_code": 422}
    
    
        
    