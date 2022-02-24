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


class Streamer(Base):
    """Streamer model for storing stream providers data"""

    __tablename__ = "streamer"
    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(db.String(64), unique=True)
    camera = relationship("Camera", back_populates="streamer", lazy="dynamic")

    def __init__(self, **kwargs):
        super(Streamer, self).__init__(**kwargs)

    def __repr__(self):
        return f"<Streamer {self.name}>"


class Camera(Base):
    """Camera model for storing camera related data"""

    __tablename__ = "camera"
    id = db.Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(db.String(64), unique=True)
    utm_x = Column(db.Float)
    utm_y = Column(db.Float)
    owner_id = Column(db.Integer, db.ForeignKey("user.id"))
    manufacturer_id = Column(GUID(), db.ForeignKey("camera_manufacturer.id"))
    manufacturer = relationship("CameraManufacturer", innerjoin=True)
    streamer_id = Column(GUID(), db.ForeignKey("streamer.id"))
    streamer = relationship("Streamer", innerjoin=True)
    resolution_x = Column(db.Integer)
    resolution_y = Column(db.Integer)
    url = Column(db.String)
    connection_date = Column(db.DateTime)
    status = Column(db.Enum(CameraStatus), nullable=False)

    def __init__(self, **kwargs):
        super(Camera, self).__init__(**kwargs)

    def __repr__(self):
        return f"<Camera {self.name}>"
