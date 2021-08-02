import os
from pathlib import Path
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    create_engine,
    Table,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

RUNNING_IN_AZURE = os.getenv("RUNNING_IN_AZURE", False)
if RUNNING_IN_AZURE:
    database_location = Path("/tmp").joinpath("database.db")
else:
    database_location = Path().cwd().joinpath("database.db")
engine_path = f"sqlite:///{database_location}"


engine = create_engine(engine_path)
Session = sessionmaker(bind=engine)
Base = declarative_base()
session = Session()


def create_tables():
    Base.metadata.create_all(engine)


class BaseModel(Base):
    __abstract__ = True

    def insert(self):
        session.add(self)
        session.commit()

    @staticmethod
    def update():
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()


participants_association_table = Table(
    "meetings_participants",
    Base.metadata,
    Column("meeting_id", ForeignKey("meeting.id"), primary_key=True),
    Column("participant_id", ForeignKey("participant.id"), primary_key=True),
)

labels_association_table = Table(
    "meetings_labels",
    Base.metadata,
    Column("meeting_id", ForeignKey("meeting.id"), primary_key=True),
    Column("label_id", ForeignKey("label.id"), primary_key=True),
)


class Meeting(BaseModel):
    __tablename__ = "meeting"
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    date = Column(DateTime, nullable=False, unique=True)
    link = Column(String(500), server_default="", default="")
    participants = relationship(
        "Participant", secondary="meetings_participants", backref="meetings"
    )
    labels = relationship("Label", secondary="meetings_labels", backref="meetings")

    def add_child(self, child):
        if child.__tablename__ == "participant":
            self.participants.append(child)
        elif child.__tablename__ == "label":
            self.labels.append(child)
        session.commit()

    def __init__(self, date, link=""):
        self.date = date
        self.link = link

    def __repr__(self):
        return (
            f"Meeting(id={self.id}, date={self.date.strftime('%B %d, %Y - %I:%M %p')})"
        )


class Participant(BaseModel):
    __tablename__ = "participant"
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    name = Column(String(80), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Participant(id={self.id}, name={self.name})"


class Label(BaseModel):
    __tablename__ = "label"
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    name = Column(String(80), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Label(id={self.id}, name={self.name})"
