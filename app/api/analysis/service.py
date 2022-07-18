import logging
import os.path
from datetime import datetime
from io import BytesIO

import requests
from flask import current_app, send_file

from app import db
from app.dbmodels.ai import Analysis
from app.dbmodels.ai import Workflow as Workflow
from app.dbmodels.schemas import AnalysisSchema
from app.utils import err_resp, internal_err_resp, message

from .utils import load_analysis_data, load_workflow_structure

logger = logging.getLogger(__name__)

analysis_schema = AnalysisSchema()


class AnalysisService:
    @staticmethod
    def get_analysis():
        """Get a list of all analysis"""
        if not (analysis := Analysis.query.all()):
            return err_resp("no analysis found", "analysis_404", 404)

        try:
            analysis_data = load_analysis_data(analysis, many=True)
            resp = message(True, "analysis data sent")
            resp["analysis"] = analysis_data

            return resp, 200

        except Exception as error:
            logger.error(error)
            return internal_err_resp()

    @staticmethod
    def create_analysis(user_id, data):
        try:

            name = data["name"]
            logger.info(f"Creating analysis with name {name}")
            if Analysis.query.filter_by(name=name).first() is not None:
                logger.error(f"Analysis with name {name} already exists")
                return err_resp("name already exists", "name_404", 404)

            workflow_id = data.get("workflow_id", None)
            logger.info(f"Analysis uses the following workflow {workflow_id}")
            # workflows are assumed to be accessible by everyone here
            if not workflow_id or not (
                workflow := Workflow.query.filter_by(id=workflow_id).first()
            ):
                return err_resp("invalid workflow", "workflow_404", 404)

            new_analysis = Analysis(
                name=name,
                creator=user_id,
                created_at=datetime.utcnow(),
                status="new",
                workflow_id=workflow.id,
            )
            # Analysis started. create a db object
            db.session.add(new_analysis)
            db.session.flush()
            db.session.commit()
            logger.info("Database item is created")

            storage_path = f"{current_app.config['USER_ASSETS']}/{user_id}/analysis/{str(new_analysis.id)}/"
            logger.info(f"Analysis results will be stored in {storage_path}")
            new_analysis.results_path = storage_path
            logger.info("Updating database item with storage path")
            # Analysis started. create a db object
            db.session.add(new_analysis)
            db.session.flush()
            db.session.commit()

            workflow_structure = f'{current_app.config["FALCOEYE_ASSETS"]}/workflows/{workflow_id}/structure.json'
            logger.info(f"Loading workflow structure from {workflow_structure}")
            wf_structure = load_workflow_structure(workflow_structure)

            wf_args = data.get("args", {})
            # This is where analysis output will be stored. Must be augmented here
            wf_args["prefix"] = storage_path
            data = {
                "analysis": {"id": str(new_analysis.id), "args": wf_args},
                "workflow": wf_structure,
            }
            workflow_service = current_app.config["WORKFLOW_HOST"]
            logger.info(
                f"Sending request to workflow server on {workflow_service}/api/analysis"
            )
            headers = {"accept": "application/json", "Content-Type": "application/json"}
            wf_resp = requests.post(
                f"{workflow_service}/api/analysis", json=data, headers=headers
            )
            logger.info(f"Response received {wf_resp.json()}")

            if wf_resp.status_code == 200:
                analysis_info = analysis_schema.dump(new_analysis)
                resp = message(True, "analysis added")
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
            logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_analysis_by_id(user_id, analysis_id):
        """Get analysis by ID"""
        if not (
            analysis := Analysis.query.filter_by(
                creator=user_id, id=analysis_id
            ).first()
        ):
            return err_resp("analysis not found", "analysis_404", 404)

        try:
            analysis_data = load_analysis_data(analysis)
            resp = message(True, "analysis data sent")
            resp["analysis"] = analysis_data

            return resp, 200
        except Exception as error:
            logger.error(error)
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
                "analysis not found",
                "analysis_404",
                404,
            )

        try:
            db.session.delete(analysis)
            db.session.commit()

            resp = message(True, "analysis deleted")
            return resp, 200

        except Exception as error:
            logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_analysis_meta_by_id(user_id, analysis_id):
        """Get analysis meta by ID"""
        if not (
            analysis := Analysis.query.filter_by(
                creator=user_id, id=analysis_id
            ).first()
        ):
            return err_resp("analysis not found", "analysis_404", 404)

        try:
            analysis_dir = (
                f'{current_app.config["USER_ASSETS"]}/{user_id}/analysis/{analysis_id}/'
            )
            if current_app.config["FS_OBJ"].isfile(f"{analysis_dir}/meta.json"):
                with current_app.config["FS_OBJ"].open(
                    os.path.relpath(f"{analysis_dir}/meta.json")
                ) as f:
                    data = f.read()
                return send_file(BytesIO(data), mimetype="application/json")
            else:
                return err_resp("no output yet", "analysis_425", 425)
        except Exception as error:
            logger.error(error)
            return internal_err_resp()
