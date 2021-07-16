import os
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = f"sqlite:///{os.path.join(project_dir, database_filename)}"

engine = create_engine(database_path)
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
        return f"Meeting<{self.id}>"


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
