from flask_restx import Namespace, fields


class MediaDto:
    api = Namespace("media", description="Media related operations.")

    video = api.model(
        "Vidoe object",
        {
            "id": fields.String,
            "name": fields.String,
            "camera_id": fields.String,
            "created_at": fields.DateTime,
            "note": fields.String,
            "tags": fields.String,
            "url": fields.String,
            "duration": fields.Integer,
        },
    )
    video_post = api.model(
        "Vidoe data post",
        {
            "name": fields.String,
            "note": fields.String,
            "tags": fields.String,
            "registry_key": fields.String,
        },
    )
    video_resp = api.model(
        "Video data response",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "video": fields.Nested(video),
        },
    )
    image = api.model(
        "Image object",
        {
            "id": fields.String,
            "name": fields.String,
            "camera_id": fields.String,
            "created_at": fields.DateTime,
            "note": fields.String,
            "tags": fields.String,
            "url": fields.String,
        },
    )
    image_post = api.model(
        "Image data post",
        {
            "name": fields.String,
            "note": fields.String,
            "tags": fields.String,
            "registry_key": fields.String,
        },
    )

    image_resp = api.model(
        "Image data response",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "image": fields.Nested(image),
        },
    )

    medial_list_item = api.model(
        "Meida list item",
        {
            "id": fields.String,
            "name": fields.String,
            "camera_id": fields.String,
            "created_at": fields.DateTime,
            "media_type": fields.String,
        },
    )
    media_resp = api.model(
        "Media List",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "media": fields.List(fields.Nested(medial_list_item)),
            "lastPage": fields.Boolean,
        },
    )
