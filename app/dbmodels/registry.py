import uuid
from datetime import datetime

from app import bcrypt, db
from app.dbmodels.base import GUID, Base

# Alias common DB names
Column = db.Column
Model = db.Model
relationship = db.relationship


class Registry(Base):
    __tablename__ = "registry"
    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user = Column(GUID(), db.ForeignKey("user.id"))
    media_type = Column(db.String)
    camera_id = Column(GUID(), db.ForeignKey("camera.id"))
    status = Column(db.String)
    created_at = Column(db.DateTime)
    capture_path = Column(db.String)
