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


logger = logging.getLogger(__name__)


@api.route("/")
class AnalysisList(Resource):
    @api.doc(
        """Get a list of all analysis""",
        responses={
            200: ("analysis data sent", AnalysisDto.analysis_list),
            404: "no analysis found",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self):
        """Get a list of all user analysis"""
        user_id = get_jwt_identity()
        return AnalysisService.get_analysis(user_id)

    @api.doc(
        "Add a new analysis",
        responses={
            201: ("analysis added", AnalysisDto.analysis_resp),
            403: "invalid workflow",
            404: "name already exists",
        },
        security="apikey",
    )
    @api.expect(AnalysisDto.analysis_post, validate=False)
    @jwt_required()
    def post(self):
        analysis_data = request.get_json()
        user_id = get_jwt_identity()
        logger.info(f"Received new analysis request from {user_id}")
        return AnalysisService.create_analysis(user_id=user_id, data=analysis_data)


@api.route("/<analysis_id>")
@api.param("analysis_id", " Analysis ID")
class Analysis(Resource):
    @api.doc(
        "Get user's analysis by id",
        responses={
            200: ("analysis data sent", AnalysisDto.analysis_resp),
            404: "analysis not found",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self, analysis_id):
        """Get an analysis"""
        current_user_id = get_jwt_identity()
        return AnalysisService.get_analysis_by_id(current_user_id, analysis_id)

    @api.doc(
        "Delete user's analysis",
        responses={
            200: "analysis deleted",
            404: "analysis not found",
        },
        security="apikey",
    )
    @jwt_required()
    def delete(self, analysis_id):
        """Delete an analysis"""
        current_user_id = get_jwt_identity()
        return AnalysisService.delete_analysis(current_user_id, analysis_id)


@api.route("/<analysis_id>/meta.json")
@api.param("analysis_id", " Analysis ID")
class Analysis(Resource):
    @api.doc(
        "Get user's analysis meta file by id",
        responses={
            404: "analysis not found",
            425: "no output yet",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self, analysis_id):
        """Get an analysis"""
        current_user_id = get_jwt_identity()
        return AnalysisService.get_analysis_meta_by_id(current_user_id, analysis_id)


@api.route("/<analysis_id>/<file_name>.<ext>")
@api.param("analysis_id", "Analysis ID")
@api.param("file_name", "File name without extension")
@api.param("ext", "File extension")
class Analysis(Resource):
    @api.doc(
        "Get user's analysis meta file by id",
        responses={
            404: "analysis not found",
            425: "no output yet",
            501: "not implemented",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self, analysis_id, file_name, ext):
        """Get an analysis"""
        current_user_id = get_jwt_identity()
        return AnalysisService.get_analysis_file_by_id(
            current_user_id, analysis_id, file_name, ext
        )
