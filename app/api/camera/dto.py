from flask_restx import Namespace, fields


class CameraDto:

    api = Namespace("camera", description="Camera related operations.")
    camera = api.model(
        "Camera Object",
        {
            "name": fields.String,
            "utm_x": fields.Float,
            "utm_y": fields.Float,
            "streamer_id": fields.String,  # youtube, angelcalm, rtsp
            "manufacturer_id": fields.String,
            # for streaming servers
            "url": fields.Url,
            # for rtsp
            "host": fields.String,
            "port": fields.Integer,
            "username": fields.String,
            "password": fields.String,
        },
    )

    camera_resp = api.model(
        "Camera Data Response",
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
            "name": fields.String,
        },
    )

    manufacturer_resp = api.model(
        "Camera Manufacturer Response",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "manufacturer": fields.Nested(camera_manufacturer),
        },
    )


class StreamerDto:

    api = Namespace("streamer", description="Camera streamer related operations.")
    camera_streamer = api.model(
        "Camera Streamer Object",
        {
            "name": fields.String,
        },
    )

    streamer_resp = api.model(
        "Camera Streamer Response",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "streamer": fields.Nested(camera_streamer),
        },
    )
