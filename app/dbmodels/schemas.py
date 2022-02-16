# Model Schemas
from app import ma


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
    class Meta:
        fields = (
            "id",
            "name",
            "utm_x",
            "utm_y",
            "manufacturer_id",
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
    class Meta:
        fields = ("id", "name", "created_at", "updated_at")
