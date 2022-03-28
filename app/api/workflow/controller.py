from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource

from app.dbmodels.schemas import WorkflowSchema
from app.utils import validation_error

from .dto import WorkflowDto
from .service import WorkflowService

api = WorkflowDto.api
workflow_resp = WorkflowDto.workflow_resp

workflow_schema = WorkflowSchema()


@api.route("/")
class WorkflowList(Resource):
    @api.doc(
        """Get a list of all workflows""",
        response={
            200: ("Workflow data succesffuly sent", workflow_resp),
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
        response={
            201: ("Successfully added workflow", workflow_resp),
            400: "Malformed data or validations failed.",
        },
        security="apikey",
    )
    @api.expect(WorkflowDto.workflow, validate=False)
    @jwt_required()
    def post(self):
        workflow_data = request.get_json()
        user_id = get_jwt_identity()
        if errors := workflow_schema.validate(workflow_data):
            return validation_error(False, errors), 400

        return WorkflowService.create_workflow(user_id=user_id, data=workflow_data)


@api.route("/<workflow_id>")
@api.param("workflow_id", " Workflow ID")
class Workflow(Resource):
    @api.doc(
        security="apikey",
    )
    @jwt_required()
    def get(self, workflow_id):
        """Get a workflow"""
        # current_user_id = get_jwt_identity()
        return WorkflowService.get_workflow_by_id(workflow_id)

    @api.doc(
        security="apikey",
    )
    @jwt_required()
    def delete(self, workflow_id):
        """Delete a workflow"""
        current_user_id = get_jwt_identity()
        return WorkflowService.delete_workflow(current_user_id, workflow_id)
