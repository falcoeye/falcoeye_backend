import logging

from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource

from app.dbmodels.schemas import AnalysisSchema
from app.utils import validation_error

from .dto import AnalysisDto
from .service import AnalysisService

api = AnalysisDto.api
analysis_schema = AnalysisSchema()


@api.route("/")
class AnalysisList(Resource):
    @api.doc(
        """Get a list of all analysiss""",
        responses={
            200: ("Analysis data sent", AnalysisDto.analysis_list),
            404: "No analysis found",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self):
        """Get a list of all system analysiss"""
        return AnalysisService.get_analysiss()

    @api.doc(
        "Add a new analysis",
        responses={
            201: ("Successfully added analysis", AnalysisDto.analysis_resp),
            403: "Invalid data.",
            404: "Invalid data. Name already exists",
        },
        security="apikey",
    )
    @api.expect(AnalysisDto.analysis_post, validate=False)
    @jwt_required()
    def post(self):
        analysis_data = request.get_json()
        user_id = get_jwt_identity()
        logging.info(f"Recevied new analysis request from {user_id}")
        return AnalysisService.create_analysis(user_id=user_id, data=analysis_data)


@api.route("/<analysis_id>")
@api.param("analysis_id", " Analysis ID")
class Analysis(Resource):
    @api.doc(
        "Get user's analysis by id",
        responses={
            200: ("Analysis data sent", AnalysisDto.analysis_resp),
            404: "Analysis not found!",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self, analysis_id):
        """Get a analysis"""
        current_user_id = get_jwt_identity()
        return AnalysisService.get_analysis_by_id(current_user_id, analysis_id)

    @api.doc(
        "Delete user's analysis",
        responses={
            200: ("Analysis successfully deleted"),
            404: "Analysis not found!",
        },
        security="apikey",
    )
    @jwt_required()
    def delete(self, analysis_id):
        """Delete a analysis"""
        current_user_id = get_jwt_identity()
        return AnalysisService.delete_analysis(current_user_id, analysis_id)
