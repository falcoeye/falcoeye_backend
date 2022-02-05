from datetime import datetime

from app import db

# Alias common DB names
Column = db.Column
Model = db.Model
relationship = db.relationship


class Dataset(Model):
    __tablename__ = "dataset"
    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(64), unique=True)
    creator = Column(db.Integer, db.ForeignKey("user.id"))
    annotation_type = Column(db.DateTime)  # xml, json, what version, ... etc
    image_width = Column(db.Integer)
    image_height = Column(db.Integer)
    size_type = Column(db.String)  # Unified or Mixed


class AIModel(Model):
    __tablename__ = "ai_model"
    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(64), unique=True)
    creator = Column(db.Integer, db.ForeignKey("user.id"))
    publish_date = Column(db.DateTime)
    archeticture = Column(db.String)  # ssd, frcnn,...etc
    backbone = Column(db.String)  # resnet, mobilenet,...etc
    dataset = Column(db.Integer, db.ForeignKey("dataset.id"))
    technology = Column(db.String)  # tensorflow or pytorch
    speed = Column(db.Integer)  # benchmarking speed


class Workflow(Model):
    __tablename__ = "workflow"
    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(64), unique=True)
    creator = Column(db.Integer, db.ForeignKey("user.id"))
    publish_date = Column(db.DateTime)
    aimodel = Column(db.Integer, db.ForeignKey("ai_model.id"))
    usedfor = Column(db.String)
    consideration = Column(db.String)
    assumption = Column(db.String)
    accepted_media = Column(db.String)  # stream | videos | images
    results_type = Column(db.String)  # csv    | videos | images
    thumpnail_url = Column(db.String)


class Analysis(Model):
    __tablename__ = "analysis"
    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(64), unique=True)
    creator = Column(db.Integer, db.ForeignKey("user.id"))
    creating_date = Column(db.DateTime)
    workflow = Column(db.Integer, db.ForeignKey("workflow.id"))
    status = Column(db.String)  # active, error, completed
    results_path = Column(db.String)
    thumpnail_url = Column(db.String)
