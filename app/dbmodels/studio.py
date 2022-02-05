from datetime import datetime

from app import bcrypt, db

# Alias common DB names
Column = db.Column
Model = db.Model
relationship = db.relationship


class Video(Model):
    __tablename__ = "video"
    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(64), unique=True)
    user = Column(db.Integer, db.ForeignKey("user.id"))
    camera = Column(db.Integer, db.ForeignKey("camera.id"))
    creation_datetime = Column(db.DateTime)
    note = Column(db.String)
    tags = Column(db.String)
    workflow = Column(db.Integer, db.ForeignKey("workflow.id"))
    duration = Column(db.Integer)


class Image(Model):
    __tablename__ = "image"
    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(64), unique=True)
    user = Column(db.Integer, db.ForeignKey("user.id"))
    camera = Column(db.Integer, db.ForeignKey("camera.id"))
    creation_datetime = Column(db.DateTime)
    note = Column(db.String)
    tags = Column(db.String)
    workflow = Column(db.Integer, db.ForeignKey("workflow.id"))
