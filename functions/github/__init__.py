from os import environ
from github import Github
from datetime import datetime
from ..models import database_location


TARGET_BRANCH = "gh-pages"
REPO_FULL_NAME = "ElGarash/Jitsi-Meetings-Dashboard"
REPO = Github(environ["GITHUB_ACCESS_TOKEN"]).get_repo(REPO_FULL_NAME)

def clone_db_file():
    db_file_metadata = REPO.get_contents("database.db", ref=TARGET_BRANCH)
    with open(database_location, "wb") as db_file:
        db_file.write(db_file_metadata.decoded_content)
    return db_file_metadata
        
        
def push_db_file(db_file_metadata):
    with open(database_location, "rb") as db_file:
        updated_content = db_file.read()
    REPO.update_file(
        path=db_file_metadata.path,
        message=f"Azure at {datetime.now().strftime('%B %d, %Y - %I:%M %p')}",
        content=updated_content,
        sha=db_file_metadata.sha,
        branch=TARGET_BRANCH,
    )