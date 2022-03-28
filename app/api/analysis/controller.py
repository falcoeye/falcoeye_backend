from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource

from app.dbmodels.schemas import AnalysisSchema
from app.utils import validation_error

from .dto import AnalysisDto
from .service import AnalysisService

api = AnalysisDto.api
analysis_resp = AnalysisDto.analysis_resp

analysis_schema = AnalysisSchema()


@api.route("/")
class AnalysisList(Resource):
    @api.doc(
        """Get a list of all analysiss""",
        response={
            200: ("Analysis data succesffuly sent", analysis_resp),
            404: "No analysiss found",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self):
        """Get a list of all system analysiss"""
        return AnalysisService.get_analysiss()

    @api.doc(
        "Add a new analysis",
        response={
            201: ("Successfully added analysis", analysis_resp),
            400: "Malformed data or validations failed.",
        },
        security="apikey",
    )
    @api.expect(AnalysisDto.analysis, validate=False)
    @jwt_required()
    def post(self):
        analysis_data = request.get_json()
        user_id = get_jwt_identity()
        if errors := analysis_schema.validate(analysis_data):
            return validation_error(False, errors), 400

        return AnalysisService.create_analysis(user_id=user_id, data=analysis_data)


@api.route("/<analysis_id>")
@api.param("analysis_id", " Analysis ID")
class Analysis(Resource):
    @api.doc(
        security="apikey",
    )
    @jwt_required()
    def get(self, analysis_id):
        """Get a analysis"""
        # current_user_id = get_jwt_identity()
        return AnalysisService.get_analysis_by_id(analysis_id)

    @api.doc(
        security="apikey",
    )
    @jwt_required()
    def delete(self, analysis_id):
        """Delete a analysis"""
        current_user_id = get_jwt_identity()
        return AnalysisService.delete_analysis(current_user_id, analysis_id)
