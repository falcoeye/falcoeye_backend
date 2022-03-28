from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource

from app.dbmodels.schemas import DatasetSchema
from app.utils import validation_error

from .dto import DatasetDto
from .service import DatasetService

api = DatasetDto.api
dataset_resp = DatasetDto.dataset_resp

dataset_schema = DatasetSchema()


@api.route("/")
class DatasetList(Resource):
    @api.doc(
        """Get a list of all datasets""",
        response={
            200: ("Dataset data succesffuly sent", dataset_resp),
            404: "No datasets found",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self):
        """Get a list of all system datasets"""
        return DatasetService.get_datasets()

    @api.doc(
        "Add a new dataset",
        response={
            201: ("Successfully added dataset", dataset_resp),
            400: "Malformed data or validations failed.",
        },
        security="apikey",
    )
    @api.expect(DatasetDto.dataset, validate=False)
    @jwt_required()
    def post(self):
        """Create new dataset"""
        dataset_data = request.get_json()
        user_id = get_jwt_identity()
        if errors := dataset_schema.validate(dataset_data):
            return validation_error(False, errors), 400

        return DatasetService.create_dataset(user_id=user_id, data=dataset_data)


@api.route("/<dataset_id>")
@api.param("dataset_id", " Dataset ID")
class Dataset(Resource):
    @api.doc(
        security="apikey",
    )
    @jwt_required()
    def delete(self, dataset_id):
        """Delete a dataset"""
        current_user_id = get_jwt_identity()
        return DatasetService.delete_dataset(current_user_id, dataset_id)

    @api.doc(
        security="apikey",
    )
    @jwt_required()
    def get(self, dataset_id):
        """get a dataset"""
        # current_user_id = get_jwt_identity()
        return DatasetService.get_dataset_by_id(dataset_id)
