from flask_restx import Namespace, fields


class DatasetDto:
    api = Namespace("dataset", description="Dataset related operations.")
    dataset = api.model(
        "Dataset Object",
        {
            "name": fields.String,
            # "creator": fields.Integer,
            "annotation_type": fields.String,
            "image_width": fields.Integer,
            "image_height": fields.Integer,
            "size_type": fields.String,
            "created_at": fields.DateTime,
            "updated_at": fields.DateTime,
        },
    )

    dataset_resp = api.model(
        "Dataset Data Response",
        {
            "status": fields.Boolean,
            "message": fields.String,
            "dataset": fields.Nested(dataset),
        },
    )
