from flask_restx import Namespace, fields


class MediaDto:
    api = Namespace("media", description="Media related operations.")
    video_post = api.model(
        "Vidoe object",
        {"note": fields.String, "tags": fields.String, "registry_key": fields.String},
    )
    video = api.model(
        "Vidoe object",
        {
            "note": fields.String,
            "tags": fields.String,
            "duration": fields.Integer,
            "url": fields.String,
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
        "Vidoe object",
        {"note": fields.String, "tags": fields.String, "url": fields.String},
    )
    image_post = api.model(
        "Image object",
        {"note": fields.String, "tags": fields.String, "registry_key": fields.String},
    )

    image_resp = api.model(
        "Image Data Response",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "image": fields.Nested(image),
        },
    )
