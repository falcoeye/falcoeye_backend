from flask import current_app

from app import db
from app.dbmodels.ai import Workflow
from app.utils import err_resp, internal_err_resp, message

from .utils import load_workflow_data


class WorkflowService:
    @staticmethod
    def get_workflows():
        """Get a list of all workflows"""
        if not (workflows := Workflow.query.all()):
            return err_resp("No workflow founds!", "workflow_404", 404)

        try:
            workflow_data = load_workflow_data(workflows, many=True)
            resp = message(True, "workflow data sent")
            resp["workflow"] = workflow_data

            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()
