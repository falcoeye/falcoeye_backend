import base64
import json
import logging
import os
import shutil
from datetime import datetime

from flask import current_app
from PIL import Image

from app import db
from app.dbmodels.ai import AIModel, Workflow
from app.dbmodels.schemas import WorkflowSchema
from app.utils import err_resp, internal_err_resp, message

from .utils import load_workflow_data, mkdir

basedir = os.path.abspath(os.path.dirname(__file__))

workflow_schema = WorkflowSchema()


class WorkflowService:
    @staticmethod
    def get_workflows():
        """Get a list of all workflows"""
        if not (workflows := Workflow.query.all()):
            return err_resp("No workflow founds!", "workflow_404", 404)

        try:
            workflow_data = load_workflow_data(workflows, many=True)
            logging.info(workflow_data)
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
            logging.info(f"Received new workflow {name}")
            if Workflow.query.filter_by(name=name).first() is not None:
                return err_resp("Name is already being used.", "name_taken", 403)

            aimodel_id = data["aimodel_id"]
            # ai models table are assumed to be accessable by everyone here
            if not (aimodel := AIModel.query.filter_by(id=aimodel_id).first()):
                return err_resp("Model not found!", "camera_404", 404)

            workflow_structre = data["structure"]

            # TODO: creation date vs publish date (which one)
            # TODO: no need for structure file anymore
            new_workflow = Workflow(
                name=data["name"],
                creator=user_id,
                publish_date=datetime.utcnow(),
                aimodel_id=aimodel.id,
                usedfor=data["usedfor"],
                consideration=data["consideration"],
                assumption=data["assumption"],
                results_description=data["results_description"],
            )

            db.session.add(new_workflow)
            db.session.flush()
            db.session.commit()

            logging.info("Workflow added to the database")

            workflow_dir = (
                f'{current_app.config["FALCOEYE_ASSETS"]}/workflows/{new_workflow.id}'
            )
            mkdir(workflow_dir)
            with open(f"{workflow_dir}/structure.json", "w") as f:
                f.write(json.dumps(workflow_structre))

            base64_img = data.get("image", None)
            workflow_img = f"{workflow_dir}/img_original.jpg"
            if base64_img:
                imgdata = base64.b64decode(base64_img)
                with open(workflow_img, "wb") as f:
                    f.write(imgdata)
            else:
                shutil.copy2(f"{basedir}/assets/default_workflow_img.jpg", workflow_img)

            # TODO: resize and save more image sizes

            workflow_info = workflow_schema.dump(new_workflow)
            resp = message(True, "Workflow has been added.")
            resp["workflow"] = workflow_info
            return resp, 201
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_workflow_by_id(workflow_id):
        """Get workflow by ID"""
        if not (workflow := Workflow.query.filter_by(id=workflow_id).first()):
            return err_resp("Workflow not found!", "workflow_404", 404)

        ai_model_name = None
        if workflow.aimodel_id:
            ai_model_name = AIModel.query.filter_by(id=workflow.aimodel_id).first().name

        try:
            workflow_data = {
                "id": workflow.id,
                "name": workflow.name,
                "creator": workflow.creator,
                "publish_date": workflow.publish_date,
                "aimodel_name": ai_model_name,
                "usedfor": workflow.usedfor,
                "consideration": workflow.consideration,
                "assumption": workflow.assumption,
            }
            resp = message(True, "Workflow data sent")
            resp["workflow"] = workflow_data

            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def delete_workflow(user_id, workflow_id):
        """Delete a workflow from DB by name and user id"""
        if not (
            workflow := Workflow.query.filter_by(
                creator=user_id, id=workflow_id
            ).first()
        ):
            return err_resp(
                "Workflow not found!",
                "workflow_404",
                404,
            )

        try:
            db.session.delete(workflow)
            db.session.commit()

            resp = message(True, "workflow deleted")
            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()
