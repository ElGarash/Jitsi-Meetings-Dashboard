import os

from flask_sqlalchemy import SQLAlchemy

database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = f"sqlite:///{os.path.join(project_dir, database_filename)}"

db = SQLAlchemy()


def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()


class Meeting(db.Model):
    __tablename__ = "meeting"
    date = db.Column(db.DateTime, nullable=False, primary_key=True)
    link = db.Column(db.String(500), server_default="", default="")
    participants = db.relationship("Participant", backref="meeting")
    labels = db.relationship("Label", backref="meeting")

    def format(self):
        return {
            "date": self.date,
            "link": self.link,
            "participants": [participant.name for participant in self.participants],
            "labels": [label.name for label in self.labels],
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class Participant(db.Model):
    __tablename__ = "participant"
    id = db.Column(db.Integer().with_variant(db.Integer, "sqlite"), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    meeting_date = db.Column(db.DateTime, db.ForeignKey("meeting.date"), nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class Label(db.Model):
    __tablename__ = "label"
    id = db.Column(db.Integer().with_variant(db.Integer, "sqlite"), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    meeting_date = db.Column(db.DateTime, db.ForeignKey("meeting.date"), nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()
