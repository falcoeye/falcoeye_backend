import base64
import io
import json
import logging
import os
from datetime import datetime

from flask import current_app
from PIL import Image
from sqlalchemy import desc

from app import db
from app.dbmodels.ai import AIModel, Workflow
from app.dbmodels.schemas import WorkflowSchema
from app.utils import err_resp, internal_err_resp, message, mkdir, put

from .utils import load_workflow_data

logger = logging.getLogger(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

workflow_schema = WorkflowSchema()

orderby_dict = {
    "name": Workflow.name,
    "creator": Workflow.creator,
    "publish_date": Workflow.publish_date,
    "name_desc": desc(Workflow.name),
    "creator_desc": desc(Workflow.creator),
    "publish_date_desc": desc(Workflow.publish_date),
}


class WorkflowService:
    @staticmethod
    def get_workflows(orderby, per_page, page, order_dir):
        """Get a list of all workflows"""
        if order_dir == "desc":
            orderby += "_desc"
        orderby = orderby_dict.get(orderby, Workflow.name)
        query = Workflow.query.order_by(orderby).paginate(page, per_page=per_page)
        if not (workflows := query.items):
            resp = message(True, "no workflow found")
            return resp, 204
        lastPage = not query.has_next
        try:
            workflow_data = load_workflow_data(workflows, many=True)
            logger.info(workflow_data)
            resp = message(True, "workflow data sent")
            resp["workflow"] = workflow_data
            resp["lastPage"] = lastPage
            return resp, 200

        except Exception as error:
            logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_workflow_count():
        """Get workflows count"""
        workflow_count = Workflow.query.count()
        try:
            resp = message(True, "workflow count data sent")
            resp["workflow_count"] = workflow_count
            return resp, 200
        except Exception as error:
            logger.error(error)
            return internal_err_resp()

    @staticmethod
    def create_workflow(user_id, data):
        new_workflow = None
        try:
            name = data["name"]
            logger.info(f"Received new workflow {name}")
            if Workflow.query.filter_by(name=name).first() is not None:
                return err_resp("name already exists", "name_taken", 403)

            workflow_structure = data["structure"]

            # TODO: creation date vs publish date (which one)
            # TODO: no need for structure file anymore
            new_workflow = Workflow(
                name=data["name"],
                creator=user_id,
                publish_date=datetime.utcnow(),
                usedfor=data["usedfor"],
                consideration=data["consideration"],
                assumption=data["assumption"],
                results_description=data["results_description"],
            )

            db.session.add(new_workflow)
            db.session.flush()
            db.session.commit()

            logger.info("Workflow added to the database")

            workflow_dir = (
                f'{current_app.config["FALCOEYE_ASSETS"]}/workflows/{new_workflow.id}/'
            )
            mkdir(workflow_dir)
            logger.info(f"Storing workflow data in {workflow_dir}")
            with current_app.config["FS_OBJ"].open(
                os.path.relpath(f"{workflow_dir}/structure.json"), "w"
            ) as f:
                f.write(json.dumps(workflow_structure))

            base64_img = data.get("image", None)
            workflow_img = f"{workflow_dir}/img_original.jpg"
            thumbnail_img = f"{workflow_dir}/img_260.jpg"
            if base64_img:
                imgdata = base64.b64decode(base64_img)
                with current_app.config["FS_OBJ"].open(
                    os.path.relpath(workflow_img), "wb"
                ) as f:
                    f.write(imgdata)

                logging.info("Adding workflow thumbnail")
                buffer = io.BytesIO()
                img = Image.open(io.BytesIO(imgdata))
                img.thumbnail((260, 260))
                img.save(buffer, format="JPEG")
                with current_app.config["FS_OBJ"].open(
                    os.path.relpath(thumbnail_img), "wb"
                ) as f:
                    f.write(buffer.getbuffer())

            else:
                logger.info("No workflow image. Copying default")
                put(f"{basedir}/assets/default_workflow_img.jpg", workflow_img)
                put(f"{basedir}/assets/default_workflow_img_260.jpg", thumbnail_img)

            # TODO: resize and save more image sizes

            workflow_info = workflow_schema.dump(new_workflow)
            resp = message(True, "workflow added")
            resp["workflow"] = workflow_info
            return resp, 201
        except Exception as error:
            if new_workflow:
                db.session.delete(new_workflow)
                db.session.flush()
                db.session.commit()

            logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_workflow_by_id(workflow_id):
        """Get workflow by ID"""

        if not (workflow := Workflow.query.filter_by(id=workflow_id).first()):
            return err_resp("workflow not found", "workflow_404", 404)

        logging.info(f"Requesting workflow {workflow_id} name {workflow.name}")

        try:
            workflow_data = {
                "id": str(workflow.id),
                "name": workflow.name,
                "creator": str(workflow.creator),
                "publish_date": workflow.publish_date.strftime("%m/%d/%Y, %H:%M:%S"),
                "usedfor": workflow.usedfor,
                "consideration": workflow.consideration,
                "assumption": workflow.assumption,
            }
            resp = message(True, "workflow data sent")
            resp["workflow"] = workflow_data

            return resp, 200

        except Exception as error:
            logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_workflow_params_by_id(workflow_id):
        """Get workflow by ID"""
        try:
            if not (workflow := Workflow.query.filter_by(id=workflow_id).first()):
                return err_resp("workflow not found", "workflow_404", 404)

            workflow_dir = (
                f'{current_app.config["FALCOEYE_ASSETS"]}/workflows/{workflow.id}/'
            )

            with current_app.config["FS_OBJ"].open(
                os.path.relpath(f"{workflow_dir}/structure.json"), "r"
            ) as f:
                workflow_structure = json.load(f)

            resp = message(True, "params sent")
            resp["workflow_params"] = workflow_structure["feeds"]
            return resp, 200

        except Exception as error:
            logger.error(error)
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
                "workflow not found",
                "workflow_404",
                404,
            )

        try:
            db.session.delete(workflow)
            db.session.commit()

            resp = message(True, "workflow deleted")
            return resp, 200

        except Exception as error:
            logger.error(error)
            return internal_err_resp()

    @staticmethod
    def update_workflow_by_id(user_id, workflow_id, data):

        if not (
            workflow := Workflow.query.filter_by(
                creator=user_id, id=workflow_id
            ).first()
        ):
            return err_resp("workflow not found", "workflow_404", 404)

        logger.info(f"Modifying workflow {workflow.name}")
        name = data.get("name", workflow.name)
        usedfor = data.get("usedfor", workflow.usedfor)
        consideration = data.get("consideration", workflow.consideration)
        results_description = data.get(
            "results_description", workflow.results_description
        )
        assumption = data.get("assumption", workflow.assumption)
        structure = data.get("structure", None)
        base64_img = data.get("image", None)

        try:
            logging.info("Updating workflow meta data in db")
            workflow.name = name
            workflow.usedfor = usedfor
            workflow.consideration = consideration
            workflow.results_description = results_description
            workflow.assumption = assumption

            db.session.flush()
            db.session.commit()
            workflow_data = load_workflow_data(workflow)

            workflow_dir = (
                f'{current_app.config["FALCOEYE_ASSETS"]}/workflows/{workflow.id}/'
            )
            logger.info(f"Updating workflow data in {workflow_dir}")

            if structure:
                logging.info("Updating workflow structure")
                with current_app.config["FS_OBJ"].open(
                    os.path.relpath(f"{workflow_dir}/structure.json"), "w"
                ) as f:
                    f.write(json.dumps(structure))

            if base64_img:
                logging.info("Updating workflow image")
                workflow_img = f"{workflow_dir}/img_original.jpg"
                imgdata = base64.b64decode(base64_img)
                with current_app.config["FS_OBJ"].open(
                    os.path.relpath(workflow_img), "wb"
                ) as f:
                    f.write(imgdata)

                logging.info("Adding workflow thumbnail")
                buffer = io.BytesIO()
                img = Image.open(io.BytesIO(imgdata))
                img.thumbnail((260, 260))
                img.save(buffer, format="JPEG")
                thumbnail_img = f"{workflow_dir}/img_260.jpg"
                with current_app.config["FS_OBJ"].open(
                    os.path.relpath(thumbnail_img), "wb"
                ) as f:
                    f.write(buffer.getbuffer())

            resp = message(True, "workflow edited")
            resp["workflow"] = workflow_data

            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()
