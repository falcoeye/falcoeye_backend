import enum

from flask_restx import Namespace, fields


class Streamer(enum.Enum):
    RTSP = "RTSP"
    StreamingServer = "StreamingServer"


class CameraDto:

    api = Namespace("camera", description="Camera related operations.")
    camera = api.model(
        "Camera object",
        {
            "id": fields.String,
            "name": fields.String,
            "utm_x": fields.Float,
            "utm_y": fields.Float,
            "streaming_type": fields.String,
            "manufacturer_id": fields.String,
            "url": fields.Url,
            "host": fields.String,
            "port": fields.Integer,
            "username": fields.String,
            "password": fields.String,
            "created_at": fields.DateTime,
        },
    )

    camera_post = api.model(
        "Camera post data",
        {
            "name": fields.String,
            "utm_x": fields.Float,
            "utm_y": fields.Float,
            "streaming_type": fields.String(enum=Streamer._member_names_),
            "manufacturer_id": fields.String,
            "url": fields.Url,
            "host": fields.String,
            "port": fields.Integer,
            "username": fields.String,
            "password": fields.String,
        },
    )

    camera_short = api.model(
        "Camera list item",
        {
            "id": fields.String,
            "name": fields.String,
            "utm_x": fields.Float,
            "utm_y": fields.Float,
            "created_at": fields.DateTime,
        },
    )

    camera_list = api.model(
        "Camera list",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "camera": fields.List(fields.Nested(camera_short)),
        },
    )

    camera_resp = api.model(
        "Camera added response",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "camera": fields.Nested(camera),
        },
    )


class CameraManufacturerDto:

    api = Namespace(
        "manufacturer", description="Camera manufacturer related operations."
    )

    camera_manufacturer = api.model(
        "Camera Manufacturer Object",
        {
            "id": fields.String,
            "name": fields.String,
        },
    )

    camera_manufacturer_post = api.model(
        "Camera Manufacturer post data",
        {"name": fields.String},
    )

    manufacturer_resp = api.model(
        "Camera Manufacturer get response",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "manufacturer": fields.Nested(camera_manufacturer),
        },
    )

    manufacturer_list = api.model(
        "Manufacturer list",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "manufacturer": fields.List(fields.Nested(camera_manufacturer)),
        },
    )
