import uuid
from datetime import datetime

from app import bcrypt, db
from app.dbmodels.base import GUID, Base

# Alias common DB names
Column = db.Column
Model = db.Model
relationship = db.relationship


class Media(Base):
    __tablename__ = "media"
    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user = Column(GUID(), db.ForeignKey("user.id"))
    camera_id = Column(GUID(), db.ForeignKey("camera.id"))
    camera = relationship("Camera", innerjoin=True)
    note = Column(db.String)
    tags = Column(db.String)
    url = Column(db.String)
    workflow_id = Column(GUID(), db.ForeignKey("workflow.id"), default=None)
    workflow = relationship("Workflow", innerjoin=True)
    duration = Column(db.Integer, default=-1)
    created_at = Column(db.DateTime)
    media_type = Column(db.String)


class Video(Base):
    __tablename__ = "video"
    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user = Column(GUID(), db.ForeignKey("user.id"))
    camera_id = Column(GUID(), db.ForeignKey("camera.id"))
    camera = relationship("Camera", innerjoin=True)
    note = Column(db.String)
    tags = Column(db.String)
    url = Column(db.String)
    workflow_id = Column(GUID(), db.ForeignKey("workflow.id"))
    workflow = relationship("Workflow", innerjoin=True)
    duration = Column(db.Integer)
    created_at = Column(db.DateTime)


class Image(Base):
    __tablename__ = "image"
    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user = Column(GUID(), db.ForeignKey("user.id"))
    camera_id = Column(GUID(), db.ForeignKey("camera.id"))
    camera = relationship("Camera", innerjoin=True)
    note = Column(db.String)
    tags = Column(db.String)
    url = Column(db.String)
    created_at = Column(db.DateTime)
    workflow_id = Column(GUID(), db.ForeignKey("workflow.id"))
    workflow = relationship("Workflow", innerjoin=True)
