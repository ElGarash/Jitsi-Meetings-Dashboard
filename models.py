import os
from pathlib import Path
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

RUNNING_IN_AZURE = os.getenv('RUNNING_IN_AZURE', False)
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


class Meeting(Base):
    __tablename__ = "meeting"
    date = Column(DateTime, nullable=False, primary_key=True)
    link = Column(String(500), server_default="", default="")
    participants = relationship("Participant", backref="meeting")
    labels = relationship("Label", backref="meeting")

    def format(self):
        return {
            "date": self.date,
            "link": self.link,
            "participants": [participant.name for participant in self.participants],
            "labels": [label.name for label in self.labels],
        }

    def insert(self):
        session.add(self)
        session.commit()

    def __repr__(self):
        return f"Meeting<{self.date.strftime('%b %d %Y %H:%M:%S')}>"


class Participant(Base):
    __tablename__ = "participant"
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    name = Column(String(80), nullable=False)
    meeting_date = Column(DateTime, ForeignKey("meeting.date"), nullable=False)

    def insert(self):
        session.add(self)
        session.commit()

    def __repr__(self):
        return f"Participant<{self.id}>"


class Label(Base):
    __tablename__ = "label"
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    name = Column(String(80), nullable=False)
    meeting_date = Column(DateTime, ForeignKey("meeting.date"), nullable=False)

    def insert(self):
        session.add(self)
        session.commit()

    def __repr__(self):
        return f"Label<{self.id}>"
