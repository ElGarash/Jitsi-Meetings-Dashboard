import os
import pathlib
import subprocess
import logging
import azure.functions as func
from datetime import datetime


from .models import Label, Participant, Meeting, create_tables, database_directory


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")
    request_body = req.get_json()
    subprocess.run(
        f"git clone -b gh-pages --single-branch https://github.com/ElGarash/Jitsi-Meetings-Dashboard {database_directory}"
    )
    os.chdir(database_directory)
    insert_into_db(request_body)
    subprocess.run(f'git commit -am "{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}"')
    ACCESS_TOKEN = os.environ["GITHUB_ACCESS_TOKEN"]
    subprocess.run(
        f"git remote set-url origin https://nooreldeensalah:{ACCESS_TOKEN}@github.com/ElGarash/Jitsi-Meetings-Dashboard.git"
    )
    subprocess.run("git push origin")
    return func.HttpResponse(
        "Successfully updated the database and pushed the changes.", status_code=200
    )


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
