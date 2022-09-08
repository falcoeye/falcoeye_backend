import logging
import os
import re

from flask import current_app, request
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
        orderby = request.args.get("orderby", "name")
        per_page = int(request.args.get("per_page", 10))
        page = int(request.args.get("page", 1))
        order_dir = request.args.get("order_dir", "asc")
        return AnalysisService.get_analysis(user_id, orderby, per_page, page, order_dir)

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


@api.route("/count")
class AnalysisListCount(Resource):
    @api.doc(
        "Get user's analysis count",
        responses={200: ("analysis count data sent", AnalysisDto.analysis_count_resp)},
        security="apikey",
    )
    @jwt_required()
    def get(self):
        """Get user's analysis count"""
        current_user_id = get_jwt_identity()
        return AnalysisService.get_user_analysis_count(current_user_id)


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


@api.route("/<string:analysis_id>/<string:user_id>/video/<file_name>.mp4")
@api.param("analysis_id", "Analysis ID")
@api.param("user_id", "User ID")
@api.param("file_name", "File name")
class AnalysisVideoServeLocal(Resource):
    @api.doc(
        "Get user's video",
        security="apikey",
    )
    @jwt_required(optional=True)
    def get(self, analysis_id, user_id, file_name):
        """Get user's video"""

        video_path = f'{current_app.config["USER_ASSETS"]}/{user_id}/analysis/{analysis_id}/{file_name}.mp4'
        logging.info(f"serving {video_path}")
        headers = request.headers

        if "range" not in headers:
            return current_app.response_class(status=400)

        size = os.stat(video_path)
        size = size.st_size
        logging.info(f"File size {size}")
        chunk_size = 10**3
        start = int(re.sub(r"\D", "", headers["range"]))
        end = min(start + chunk_size, size - 1)

        content_lenght = end - start + 1
        logging.info(f"Content Length {content_lenght}")

        def get_chunk(video_path, start, end):
            with open(video_path, "rb") as f:
                f.seek(start)
                chunk = f.read(end)
            return chunk

        headers = {
            "Content-Range": f"bytes {start}-{end}/{size}",
            "Accept-Ranges": "bytes",
            "Content-Length": content_lenght,
            "Content-Type": "video/mp4",
        }

        return current_app.response_class(
            get_chunk(video_path, start, end), 206, headers
        )
