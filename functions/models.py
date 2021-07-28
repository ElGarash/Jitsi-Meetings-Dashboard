import os
from pathlib import Path
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
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


class Meeting(BaseModel):
    __tablename__ = "meeting"
    date = Column(DateTime, nullable=False, primary_key=True)
    link = Column(String(500), server_default="", default="")
    participants = relationship("Participant", backref="meeting")
    labels = relationship("Label", backref="meeting")

    def __repr__(self):
        return f"Meeting<{self.date.strftime('%B %d, %Y - %I:%M %p')}>"


class Participant(BaseModel):
    __tablename__ = "participant"
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    name = Column(String(80), nullable=False)
    meeting_date = Column(DateTime, ForeignKey("meeting.date"), nullable=False)

    def __repr__(self):
        return f"Participant<{self.id}>"


class Label(BaseModel):
    __tablename__ = "label"
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    name = Column(String(80), nullable=False)
    meeting_date = Column(DateTime, ForeignKey("meeting.date"), nullable=False)

    def __repr__(self):
        return f"Label<{self.id}>"
