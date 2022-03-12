# Model Schemas
import uuid

import marshmallow as ma
from marshmallow_sqlalchemy.convert import ModelConverter

from .base import GUID
from .studio import Image as Image
from .studio import Video as Video
from .user import User as User


class GUIDConverter(ModelConverter):
    SQLA_TYPE_MAPPING = dict(
        list(ModelConverter.SQLA_TYPE_MAPPING.items()) + [(GUID, ma.fields.Str)]
    )


class GUIDSerializationField(ma.fields.Field):
    def _serialize(self, value, attr, obj):
        if value is None:
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            else:
                return None


class UserSchema(ma.Schema):
    class Meta:
        fields = ("email", "name", "username", "joined_date", "role_id")


class VideoSchema(ma.Schema):
    # id = GUIDSerializationField(attribute="guid",required=True)
    camera_id = GUIDSerializationField(attribute="camera_id", required=True)
    # user = GUIDSerializationField(attribute="user", required=True)
    notes = ma.fields.Str(required=False)
    tags = ma.fields.Str(required=False)
    duration = ma.fields.Int(required=True)
    workflow = GUIDSerializationField(attribute="workflow", required=False)

    class Meta:
        model_converter = GUIDConverter
        fields = (
            "camera_id",
            "user",
            "note",
            "tags",
            "duration",
            "workflow",
            "created_at",
        )


class ImageSchema(ma.Schema):
    # id = GUIDSerializationField(attribute="guid",required=True)
    camera_id = GUIDSerializationField(attribute="camera_id", required=True)
    # user = GUIDSerializationField(attribute="user",required=True)
    note = ma.fields.Str(required=False)
    tags = ma.fields.Str(required=False)
    workflow = GUIDSerializationField(attribute="workflow", required=False)

    class Meta:
        model_converter = GUIDConverter
        fields = (
            "camera_id",
            "user",
            "note",
            "tags",
            "workflow",
            "created_at",
        )


class CameraSchema(ma.Schema):
    # id = GUIDSerializationField(attribute="guid", required=True)
    name = ma.fields.Str(required=False)
    manufacturer_id_id = GUIDSerializationField(
        attribute="manufacturer_id", required=True
    )
    streamer_id = GUIDSerializationField(attribute="streamer_id", required=True)
    url = ma.fields.Str(required=False)

    class Meta:
        fields = (
            "id",
            "name",
            "utm_x",
            "utm_y",
            "manufacturer_id",
            "streamer_id",
            "owner_id",
            "resolution_x",
            "resolution_y",
            "url",
            "connection_date",
            "status",
            "created_at",
            "updated_at",
        )


class CameraManufacturerSchema(ma.Schema):
    # id = GUIDSerializationField(attribute="guid", required=True)
    name = ma.fields.Str(required=False)

    class Meta:
        fields = ("id", "name", "created_at", "updated_at")


class StreamerSchema(ma.Schema):
    # id = GUIDSerializationField(attribute="guid", required=True)
    name = ma.fields.Str(required=False)

    class Meta:
        fields = ("id", "name", "created_at", "updated_at")


class WorkflowSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "name",
            "creator",
            "publish_date",
            "aimodel_id",
            "usedfor",
            "consideration",
            "assumption",
            "accepted_media",
            "results_type",
            "thumbnail_url",
            "created_at",
            "updated_at",
        )


class DatasetSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "name",
            "creator",
            "annotation_type",
            "image_width",
            "image_height",
            "size_type",
            "created_at",
            "updated_at",
        )


class AIModelSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "name",
            "creator",
            "publish_date",
            "archeticture",
            "backbone",
            "dataset_id",
            "technology",
            "speed",
            "created_at",
            "updated_at",
        )


class AnalysisSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "name",
            "creator",
            "creating_date",
            "workflow_id",
            "status",
            "results_path",
            "thumbnail_url",
            "created_at",
            "updated_at",
        )
