from datetime import datetime

from app import db

# Alias common DB names
Column = db.Column
Model = db.Model
relationship = db.relationship


class Camera(Model):
    __tablename__ = "camera"
    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(64), unique=True)
    utmx = Column(db.Float)
    utmy = Column(db.Float)
    owner = Column(db.String)
    manufacturer = Column(db.String)
    resolutionX = Column(db.Integer)
    resolutionY = Column(db.Integer)
    url = Column(db.String)
    connection_date = Column(db.DateTime)
    status = Column(db.String)  # running, under maintanance, disconnected,...etc
