from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource

from app.dbmodels.schemas import WorkflowSchema
from app.utils import validation_error

from .dto import WorkflowDto
from .service import WorkflowService

api_workflow = WorkflowDto.api
workflow_resp = WorkflowDto.workflow_resp

workflow_schema = WorkflowSchema()


@api_workflow.route("/")
class WorkflowList(Resource):
    @api_workflow.doc(
        """Get a list of all workflows""",
        response={
            200: ("Workflow data succesffuly sent", workflow_resp),
            404: "No workflows found",
        },
    )
    # @jwt_required()
    def get(self):
        """Get a list of all system workflows"""
        return WorkflowService.get_workflows()
