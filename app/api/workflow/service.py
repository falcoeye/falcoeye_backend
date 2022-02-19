from datetime import datetime

from flask import current_app

from app import db
from app.dbmodels.ai import Workflow
from app.dbmodels.schemas import WorkflowSchema
from app.utils import err_resp, internal_err_resp, message

from .utils import load_workflow_data

workflow_schema = WorkflowSchema()


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

    @staticmethod
    def create_workflow(user_id, data):

        try:
            name = data["name"]
            if Workflow.query.filter_by(name=name).first() is not None:
                return err_resp("Name is already being used.", "name_taken", 403)
            new_workflow = Workflow(
                name=data["name"],
                creator=user_id,
                publish_date=datetime.utcnow(),
                aimodel=data["aimodel"],
                usedfor=data["usedfor"],
                consideration=data["consideration"],
                assumption=data["assumption"],
                accepted_media=data["accepted_media"],
                results_type=data["results_type"],
                thumbnail_url=data["thumbnail_url"],
            )
            db.session.add(new_workflow)
            db.session.flush()
            db.session.commit()

            workflow_info = workflow_schema.dump(new_workflow)
            resp = message(True, "Workflow has been added.")
            resp["workflow"] = workflow_info
            return resp, 201
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()
