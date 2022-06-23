import logging

from flask import current_app, request, send_from_directory
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource

from app.dbmodels.schemas import WorkflowSchema
from app.utils import validation_error

from .dto import WorkflowDto
from .service import WorkflowService

api = WorkflowDto.api

workflow_schema = WorkflowSchema()


@api.route("/")
class WorkflowList(Resource):
    @api.doc(
        """Get a list of all workflows""",
        responses={
            200: ("Workflow data succesffuly sent", WorkflowDto.workflow_list),
            404: "No workflows found",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self):
        """Get a list of all system workflows"""
        return WorkflowService.get_workflows()

    @api.doc(
        "Add a new workflow",
        responses={
            201: ("Successfully added workflow", WorkflowDto.workflow_resp),
            400: "Malformed data or validations failed.",
        },
        security="apikey",
    )
    @api.expect(WorkflowDto.workflow_post_data, validate=False)
    @jwt_required()
    def post(self):
        workflow_data = request.get_json()
        user_id = get_jwt_identity()
        logging.info(f"Received new workflow from {user_id}")
        # if errors := workflow_schema.validate(workflow_data):
        #     return validation_error(False, errors), 400

        return WorkflowService.create_workflow(user_id=user_id, data=workflow_data)


@api.route("/<workflow_id>")
@api.param("workflow_id", " Workflow ID")
class Workflow(Resource):
    @api.doc(
        "Show a worfklow item",
        responses={
            200: ("Workflow data successfully sent", WorkflowDto.workflow_resp),
            404: "No workflow found!",
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
            200: ("Workflow successfully deleted"),
            404: "Workflow not found!",
        },
        security="apikey",
    )
    @jwt_required()
    def delete(self, workflow_id):
        """Delete a workflow"""
        current_user_id = get_jwt_identity()
        return WorkflowService.delete_workflow(current_user_id, workflow_id)


@api.route("/<workflow_id>/img_<img_size>.jpg")
@api.param("workflow_id", " Workflow ID")
@api.param("img_size", " Image Size")
class Workflow(Resource):
    @api.doc(
        "Show a worfklow item",
        responses={
            200: ("Workflow data successfully sent", WorkflowDto.workflow_resp),
            404: "No workflow found!",
        },
        security="apikey",
    )
    @jwt_required()
    def get(self, workflow_id, img_size):
        """Get a workflow"""
        # current_user_id = get_jwt_identity()
        return send_from_directory(
            f'{current_app.config["FALCOEYE_ASSETS"]}/workflows/{workflow_id}',
            f"img_{img_size}.jpg",
            mimetype="image/jpg",
        )
