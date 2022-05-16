import uuid
from datetime import datetime

from app import db
from app.dbmodels.base import GUID, Base

# Alias common DB names
Column = db.Column
Model = db.Model
relationship = db.relationship


class Dataset(Base):
    __tablename__ = "dataset"
    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(db.String(64), unique=True)
    creator = Column(GUID(), db.ForeignKey("user.id"))
    annotation_type = Column(db.String)  # xml, json, what version, ... etc
    image_width = Column(db.Integer)
    image_height = Column(db.Integer)
    size_type = Column(db.String)  # Unified or Mixed


class AIModel(Base):
    __tablename__ = "ai_model"
    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(db.String(64), unique=True)
    creator = Column(GUID(), db.ForeignKey("user.id"))
    publish_date = Column(db.DateTime)
    architecture = Column(db.String)  # ssd, frcnn,...etc
    backbone = Column(db.String)  # resnet, mobilenet,...etc
    dataset_id = Column(GUID(), db.ForeignKey("dataset.id"))
    dataset = relationship("Dataset", innerjoin=True)
    technology = Column(db.String)  # tensorflow or pytorch
    speed = Column(db.Integer)  # benchmarking speed


class Workflow(Base):
    __tablename__ = "workflow"
    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(db.String(64), unique=True)
    creator = Column(GUID(), db.ForeignKey("user.id"))
    publish_date = Column(db.DateTime)
    aimodel_id = Column(GUID(), db.ForeignKey("ai_model.id"))
    aimodel = relationship("AIModel", innerjoin=True)
    structure_file = Column(db.String)
    usedfor = Column(db.String)
    consideration = Column(db.String)
    assumption = Column(db.String)
    accepted_media = Column(db.String)  # stream | videos | images
    results_description = Column(db.String)
    results_type = Column(db.String)  # csv    | videos | images
    thumbnail_url = Column(db.String)


class Analysis(Base):
    __tablename__ = "analysis"
    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(db.String(64), unique=True)
    creator = Column(GUID(), db.ForeignKey("user.id"))
    created_at = Column(db.DateTime)
    workflow_id = Column(GUID(), db.ForeignKey("workflow.id"))
    workflow = relationship("Workflow", innerjoin=True)
    status = Column(db.String)  # new, active, error, completed
    results_path = Column(db.String)
