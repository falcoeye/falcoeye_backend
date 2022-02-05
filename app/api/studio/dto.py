from flask_restx import Namespace, fields


class MediaDto:
    api = Namespace("media", description="Media related operations.")
    video = api.model(
        "Vidoe object",
        {
            "camera": fields.Integer,
            "name": fields.String,
            "user": fields.Integer,
            "note": fields.String,
            "tags": fields.String,
            "duration": fields.Integer,
            "workflow": fields.String,
            "creation_datetime": fields.DateTime,
        },
    )
    video_resp = api.model(
        "Video Data Response",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "video": fields.Nested(video),
        },
    )
    image = api.model(
        "Image object",
        {
            "camera": fields.Integer,
            "name": fields.String,
            "user": fields.Integer,
            "note": fields.String,
            "tags": fields.String,
            "workflow": fields.String,
            "creation_datetime": fields.DateTime,
        },
    )

    image_resp = api.model(
        "Image Data Response",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "image": fields.Nested(image),
        },
    )
