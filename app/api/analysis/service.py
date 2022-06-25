import json
from datetime import datetime

import requests
from flask import current_app

from app import db
from app.dbmodels.ai import Analysis
from app.dbmodels.ai import Workflow as Workflow
from app.dbmodels.schemas import AnalysisSchema
from app.utils import err_resp, internal_err_resp, message

from .utils import load_analysis_data, load_workflow_structure

analysis_schema = AnalysisSchema()


class AnalysisService:
    @staticmethod
    def get_analysiss():
        """Get a list of all analysiss"""
        if not (analysiss := Analysis.query.all()):
            return err_resp("No analysis founds!", "analysis_404", 404)

        try:
            analysis_data = load_analysis_data(analysiss, many=True)
            resp = message(True, "Analysis data sent")
            resp["analysis"] = analysis_data

            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def create_analysis(user_id, data):
        try:
            workflow_hostname = current_app.config["WORKFLOW_HOST"]
            name = data["name"]
            if Analysis.query.filter_by(name=name).first() is not None:
                return err_resp("Invalid data. Name already exists", "name_404", 404)

            workflow_id = data.get("workflow_id", None)

            # workflows are assumed to be accessable by everyone here
            if not workflow_id or not (
                workflow := Workflow.query.filter_by(id=workflow_id).first()
            ):
                return err_resp("Invalid data.", "workflow_404", 404)

            new_analysis = Analysis(
                name=name,
                creator=user_id,
                created_at=datetime.utcnow(),
                status="new",
                workflow_id=workflow.id,
            )
            storage_path = (
                f"{current_app.config['USER_ASSETS']}/analysis/{new_analysis.id}"
            )
            new_analysis.results_path = storage_path

            # Analysis started. create a db object
            db.session.add(new_analysis)
            db.session.flush()
            db.session.commit()

            workflow_structure = f'{current_app.config["FALCOEYE_ASSETS"]}/workflows/{workflow_id}/structure.json'

            wf_structure = load_workflow_structure(workflow_structure)
            wf_args = data.get("args", {})
            # This is where analysis output will be stored. Must be augmented here
            wf_args["prefix"] = storage_path
            data = {
                "analysis": {"id": str(new_analysis.id), "args": wf_args},
                "workflow": wf_structure,
            }
            wf_resp = requests.post(
                f"{current_app.config['WORKFLOW_HOST']}/api/analysis",
                data=json.dumps(data),
            )

            if wf_resp.status_code == 200:
                analysis_info = analysis_schema.dump(new_analysis)
                resp = message(True, "Analysis has been added.")
                resp["analysis"] = analysis_info
                return resp, 201
            else:
                err_resp(
                    "Something went wrong. Couldn't start the workflow",
                    "analysis_403",
                    403,
                )
                return err_resp, 403

        except Exception as error:
            raise
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_analysis_by_id(user_id, analysis_id):
        """Get analysis by ID"""
        if not (
            analysis := Analysis.query.filter_by(
                creator=user_id, id=analysis_id
            ).first()
        ):
            return err_resp("Analysis not found!", "analysis_404", 404)

        try:
            analysis_data = load_analysis_data(analysis)
            resp = message(True, "Analysis data sent")
            resp["analysis"] = analysis_data

            return resp, 200
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def delete_analysis(user_id, analysis_id):
        """Delete a analysis from DB by name and user id"""
        if not (
            analysis := Analysis.query.filter_by(
                creator=user_id, id=analysis_id
            ).first()
        ):
            return err_resp(
                "Analysis not found!",
                "analysis_404",
                404,
            )

        try:
            db.session.delete(analysis)
            db.session.commit()

            # TODO: delete data here
            resp = message(True, "analysis deleted")
            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()
