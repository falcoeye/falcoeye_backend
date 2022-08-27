import logging
import os
from io import BytesIO

from flask import current_app, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource

from app.dbmodels.schemas import WorkflowSchema

from .dto import WorkflowDto
from .service import WorkflowService

logger = logging.getLogger(__name__)

api = WorkflowDto.api

workflow_schema = WorkflowSchema()


@api.route("/")
class WorkflowList(Resource):
    @api.doc(
        """Get a list of all workflows""",
        responses={
            200: ("workflow data sent", WorkflowDto.workflow_list),
            404: "no workflows found",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self):
        """Get a list of all system workflows"""
        orderby = request.args.get("orderby", "created_at")
        per_page = int(request.args.get("per_page", 10))
        page = int(request.args.get("page", 1))
        order_dir = request.args.get("order_dir", "asc")
        return WorkflowService.get_workflows(orderby, per_page, page, order_dir)

    @api.doc(
        "Add a new workflow",
        responses={
            201: ("workflow added", WorkflowDto.workflow_resp),
            403: "name already exists",
            400: "malformed data or validations failed",
        },
        security="apikey",
    )
    @api.expect(WorkflowDto.workflow_post_data, validate=False)
    @jwt_required()
    def post(self):
        workflow_data = request.get_json()
        user_id = get_jwt_identity()
        logger.info(f"Received new workflow from {user_id}")
        # if errors := workflow_schema.validate(workflow_data):
        #     return validation_error(False, errors), 400

        return WorkflowService.create_workflow(user_id=user_id, data=workflow_data)


@api.route("/<workflow_id>")
@api.param("workflow_id", " Workflow ID")
class Workflow(Resource):
    @api.doc(
        "Get workflow's data",
        responses={
            200: ("workflow data sent", WorkflowDto.workflow_resp),
            404: "workflow not found",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self, workflow_id):
        """Get a workflow"""
        # current_user_id = get_jwt_identity()
        return WorkflowService.get_workflow_by_id(workflow_id)

    @api.doc(
        "Delete a workflow",
        responses={
            200: "workflow deleted",
            404: "workflow not found",
        },
        security="apikey",
    )
    @jwt_required()
    def delete(self, workflow_id):
        """Delete a workflow"""
        current_user_id = get_jwt_identity()
        return WorkflowService.delete_workflow(current_user_id, workflow_id)

    @api.doc(
        "Edit user's workflow",
        responses={
            200: ("workflow edited", WorkflowDto.workflow_resp),
            404: "workflow not found",
        },
        security="apikey",
    )
    @api.expect(WorkflowDto.workflow_post_data, validate=False)
    @jwt_required()
    def put(self, workflow_id):
        """Update user's workflow"""
        workflow_data = request.get_json()
        current_user_id = get_jwt_identity()
        return WorkflowService.update_workflow_by_id(
            current_user_id, workflow_id, workflow_data
        )


@api.route("/<workflow_id>/img_<img_size>.jpg")
@api.param("workflow_id", " Workflow ID")
@api.param("img_size", " Image Size")
class Workflow(Resource):
    @api.doc(
        "Get workflow's thumbnail image",
        security="apikey",
    )
    @jwt_required()
    def get(self, workflow_id, img_size):
        """Get workflow's thumbnail image"""
        # current_user_id = get_jwt_identity()

        with current_app.config["FS_OBJ"].open(
            os.path.relpath(
                os.path.join(
                    f'{current_app.config["FALCOEYE_ASSETS"]}/workflows/{workflow_id}',
                    f"img_{img_size}.jpg",
                )
            )
        ) as f:
            img = f.read()

        return send_file(BytesIO(img), mimetype="image/jpg")


@api.route("/<workflow_id>/params")
@api.param("workflow_id", " Workflow ID")
class Workflow(Resource):
    @api.doc(
        "Get workflow's params",
        security="apikey",
        responses={
            200: ("params sent", WorkflowDto.workflow_params),
            404: "workflow not found",
        },
    )
    @jwt_required()
    def get(self, workflow_id):
        """Get workflow's params"""
        # current_user_id = get_jwt_identity()
        return WorkflowService.get_workflow_params_by_id(workflow_id)
