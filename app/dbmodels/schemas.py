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
            "id",
            "camera",
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
        fields = ("id", "duration", "creation_datetime")


class ImageSchema(ma.Schema):
    class Meta:
        # Fields to expose, add more if needed.
        fields = (
            "id",
            "camera",
            "user",
            "note",
            "tags",
            "workflow",
            "creation_datetime",
        )


class ImageSchemaShort(ma.Schema):
    class Meta:
        # Fields to expose, add more if needed.
        fields = ("id", "camera", "creation_datetime")
