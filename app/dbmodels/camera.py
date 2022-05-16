import enum
import uuid

import app
from app import db
from app.dbmodels.base import GUID, Base

from .base import GUID, Base

# Alias common DB names
Column = db.Column
relationship = db.relationship


class CameraStatus(str, enum.Enum):
    RUNNING = 1
    DISCONNECTED = 2
    UNDER_MAINTENANCE = 3


class CameraManufacturer(Base):
    """Manufacturer model for storing camera manufacturer data"""

    __tablename__ = "camera_manufacturer"
    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(db.String(64), unique=True)
    camera = relationship("Camera", back_populates="manufacturer", lazy="dynamic")

    def __init__(self, **kwargs):
        super(CameraManufacturer, self).__init__(**kwargs)

    def __repr__(self):
        return f"<CameraManufacturer {self.name}>"


class Camera(Base):
    """Camera model for storing camera related data"""

    __tablename__ = "camera"
    id = db.Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(db.String(64), unique=True)
    latitude = Column(db.Float)
    longitude = Column(db.Float)
    owner_id = Column(GUID(), db.ForeignKey("user.id"))
    manufacturer_id = Column(GUID(), db.ForeignKey("camera_manufacturer.id"))
    manufacturer = relationship("CameraManufacturer", innerjoin=True)
    streaming_type = Column(db.String)
    url = Column(db.String)
    username = Column(db.String)
    password = Column(db.String)
    host = Column(db.String)
    port = Column(db.Integer)
    created_at = Column(db.DateTime)
    status = Column(db.Enum(CameraStatus), nullable=False)

    def __init__(self, **kwargs):
        super(Camera, self).__init__(**kwargs)

    def __repr__(self):
        return f"<Camera {self.name}>"
