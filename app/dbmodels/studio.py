import uuid
from datetime import datetime

from app import bcrypt, db
from app.dbmodels.base import GUID, Base

# Alias common DB names
Column = db.Column
Model = db.Model
relationship = db.relationship


class Video(Base):
    __tablename__ = "video"
    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user = Column(db.Integer, db.ForeignKey("user.id"))
    camera_id = Column(GUID(), db.ForeignKey("camera.id"))
    camera = relationship("Camera", innerjoin=True)
    note = Column(db.String)
    tags = Column(db.String)
    workflow = Column(GUID(), db.ForeignKey("workflow.id"))
    duration = Column(db.Integer)


class Image(Base):
    __tablename__ = "image"
    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user = Column(db.Integer, db.ForeignKey("user.id"))
    camera_id = Column(GUID(), db.ForeignKey("camera.id"))
    camera = relationship("Camera", innerjoin=True)
    note = Column(db.String)
    tags = Column(db.String)
    workflow = Column(GUID(), db.ForeignKey("workflow.id"))
