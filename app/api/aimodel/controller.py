from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource

from app.dbmodels.schemas import AIModelSchema
from app.utils import validation_error

from .dto import AIModelDto
from .service import AIModelService

api = AIModelDto.api
aimodel_resp = AIModelDto.aimodel_resp

aimodel_schema = AIModelSchema()


@api.route("/")
class AIModelList(Resource):
    @api.doc(
        """Get a list of all aimodels""",
        response={
            200: ("AIModel data succesffuly sent", aimodel_resp),
            404: "No aimodels found",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self):
        """Get a list of all system aimodels"""
        return AIModelService.get_aimodels()

    @api.doc(
        "Add a new aimodel",
        response={
            201: ("Successfully added aimodel", aimodel_resp),
            400: "Malformed data or validations failed.",
        },
        security="apikey",
    )
    @api.expect(AIModelDto.aimodel, validate=False)
    @jwt_required()
    def post(self):
        aimodel_data = request.get_json()
        user_id = get_jwt_identity()
        if errors := aimodel_schema.validate(aimodel_data):
            return validation_error(False, errors), 400

        return AIModelService.create_aimodel(user_id=user_id, data=aimodel_data)


@api.route("/<aimodel_id>")
@api.param("aimodel_id", " AIModel ID")
class AIModel(Resource):
    @api.doc(
        security="apikey",
    )
    @jwt_required()
    def get(self, aimodel_id):
        """Get a aimodel"""
        # current_user_id = get_jwt_identity()
        return AIModelService.get_aimodel_by_id(aimodel_id)

    @api.doc(
        security="apikey",
    )
    @jwt_required()
    def delete(self, aimodel_id):
        """Delete a aimodel"""
        current_user_id = get_jwt_identity()
        return AIModelService.delete_aimodel(current_user_id, aimodel_id)
