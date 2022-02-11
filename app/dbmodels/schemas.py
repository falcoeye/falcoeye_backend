# Model Schemas
from app import ma

from .studio import Image as Image
from .studio import Video as Video
from .user import User as User


class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose, add more if needed.
        fields = ("email", "name", "username", "joined_date", "role_id")


class VideoSchema(ma.Schema):
    class Meta:
        # Fields to expose, add more if needed.
        fields = (
            "camera",
            "name",
            "user",
            "note",
            "tags",
            "duration",
            "workflow",
            "creation_datetime",
        )


class VideoSchemaShort(ma.Schema):
    class Meta:
        # Fields to expose, add more if needed.
        fields = ("name", "duration", "creation_datetime")


class ImageSchema(ma.Schema):
    class Meta:
        # Fields to expose, add more if needed.
        fields = (
            "camera",
            "name",
            "user",
            "note",
            "tags",
            "workflow",
            "creation_datetime",
        )


class ImageSchemaShort(ma.Schema):
    class Meta:
        # Fields to expose, add more if needed.
        fields = ("name", "creation_datetime")


class CameraSchema(ma.Schema):
    fields = (
        "id",
        "name",
        "utm_x",
        "utm_y",
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
    fields = ("id", "name", "created_at", "updated_at")
