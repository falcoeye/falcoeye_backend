import json
import logging
import os.path
from datetime import datetime
from io import BytesIO

import requests
from flask import current_app, request, send_file
from sqlalchemy import desc

from app import db
from app.dbmodels.ai import Analysis
from app.dbmodels.ai import Workflow as Workflow
from app.dbmodels.camera import Camera
from app.dbmodels.schemas import AnalysisSchema
from app.dbmodels.studio import Image as Image
from app.dbmodels.studio import Media as Media
from app.dbmodels.studio import Video as Video
from app.dbmodels.user import Permission, User
from app.utils import (
    err_resp,
    exists,
    generate_download_signed_url_v4,
    get_service,
    internal_err_resp,
    message,
    mkdir,
    random_string,
    rmtree,
)

from .utils import load_analysis_data, load_workflow_structure

logger = logging.getLogger(__name__)

analysis_schema = AnalysisSchema()


orderby_dict = {
    "name": Analysis.name,
    "creator": Analysis.creator,
    "created_at": Analysis.created_at,
    "workflow_id": Analysis.workflow_id,
    "status": Analysis.status,
    "name_desc": desc(Analysis.name),
    "creator_desc": desc(Analysis.creator),
    "created_at_desc": desc(Analysis.created_at),
    "workflow_id_desc": desc(Analysis.workflow_id),
    "status_desc": desc(Analysis.status),
}


class AnalysisService:
    @staticmethod
    def get_analysis(user_id, orderby, per_page, page, order_dir, inline):
        """Get a list of all user analysis"""
        if order_dir == "desc":
            orderby += "_desc"
        orderby = orderby_dict.get(orderby, Media.created_at)
        query = (
            Analysis.query.filter_by(creator=user_id, inline=inline)
            .order_by(orderby)
            .paginate(page, per_page=per_page)
        )
        if not (analysis := query.items):
            resp = message(True, "analysis data sent")
            resp["analysis"] = []
            resp["lastPage"] = True
            return resp, 200

        lastPage = not query.has_next
        try:
            analysis_data = load_analysis_data(analysis, many=True)
            if len(analysis_data) == 0:
                resp = message(True, "analysis data sent")
                resp["analysis"] = []
                resp["lastPage"] = True
                return resp, 200
            else:
                resp = message(True, "analysis data sent")
                resp["analysis"] = analysis_data
                resp["lastPage"] = lastPage

            return resp, 200

        except Exception as error:
            logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_user_analysis_count(user_id):
        """Get user data by username"""
        analysis_count = Analysis.query.filter_by(creator=user_id).count()
        try:
            resp = message(True, "analysis count data sent")
            resp["analysis_count"] = analysis_count
            return resp, 200
        except Exception as error:
            logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_source(wf_source, user_id):
        source_id = wf_source["id"]
        if wf_source["type"] == "video":
            if video := Media.query.filter_by(
                user=user_id, id=source_id, media_type="video"
            ).first():
                video_dir = (
                    f'{current_app.config["USER_ASSETS"]}/{user_id}/videos/{source_id}'
                )
                video_path = f"{video_dir}/video_original.mp4"
                return {"filename": video_path}
        elif wf_source["type"] == "image":
            return None
        elif wf_source["type"] == "streaming_source":
            if camera := Camera.query.filter_by(owner_id=user_id, id=source_id).first():
                return camera.con_to_json()
        return None

    @staticmethod
    def execute_workflow(user_id, wf_structure, data, storage_path, analysis_id):

        logger.info("parsing feeds")
        # parsing feeds
        feeds = data.get("feeds", None)
        if not feeds:
            return err_resp("invalid workflow", "workflow_404", 404)
        # TODO: check for bad inputs
        wf_params = feeds["params"]
        wf_source = feeds["source"]
        if wf_source["type"] not in wf_structure["feeds"]["sources"]:
            return err_resp("invalid workflow", "workflow_404", 404)
        # getting actual source data
        wf_source = AnalysisService.get_source(wf_source, user_id)
        logging.info(f"Calculated sources {wf_source}")

        # preparing args starting with params
        wf_args = wf_params
        # this is where analysis output will be stored. Must be augmented here
        wf_args["prefix"] = storage_path
        # putting source
        wf_args.update(wf_source)

        anal_data = {
            "analysis": {"id": analysis_id, "args": wf_args},
            "workflow": wf_structure,
        }
        anal_structure = f"{storage_path}/structure.json"

        with open(anal_structure, "w") as f:
            f.write(json.dumps(anal_data, indent=4))

        workflow_service = get_service(
            "falcoeye-workflow"
        )  # current_app.config["WORKFLOW_HOST"]
        logger.info(
            f"Sending request to workflow server on {workflow_service}/api/analysis"
        )
        headers = {"accept": "application/json", "Content-Type": "application/json"}

        wf_resp = requests.post(
            f"{workflow_service}/api/analysis/",
            json={"analysis_file": anal_structure},
            headers=headers,
        )

        logger.info(f"Response received {wf_resp.json()}")
        return wf_resp

    @staticmethod
    def create_analysis_(user_id, wf_id, wf_structure, data, inline):
        name = data.get("name", random_string(10))
        logger.info(f"Creating analysis with name {name}")
        if Analysis.query.filter_by(name=name).first() is not None:
            logger.error(f"Analysis with name {name} already exists")
            return err_resp("name already exists", "name_404", 404)

        new_analysis = None
        storage_path = None
        try:
            new_analysis = Analysis(
                name=name,
                creator=user_id,
                created_at=datetime.utcnow(),
                status="new",
                workflow_id=wf_id,
                inline=inline,
            )
            # Analysis started. create a db object
            db.session.add(new_analysis)
            db.session.flush()
            db.session.commit()
            logger.info("Database item is created")
            if not inline:
                storage_path = f"{current_app.config['USER_ASSETS']}/{user_id}/analysis/{str(new_analysis.id)}/"
            else:
                storage_path = f"{current_app.config['TEMPORARY_DATA_PATH']}/{user_id}/analysis/{str(new_analysis.id)}/"
            mkdir(storage_path)
            logger.info(f"Analysis results will be stored in {storage_path}")

            new_analysis.results_path = storage_path
            logger.info("Updating database item with storage path")
            # Analysis started. create a db object
            db.session.add(new_analysis)
            db.session.flush()
            db.session.commit()

            wf_resp = AnalysisService.execute_workflow(
                user_id, wf_structure, data, storage_path, str(new_analysis.id)
            )

            if wf_resp.status_code == 200:
                analysis_info = analysis_schema.dump(new_analysis)
                resp = message(True, "analysis added")
                resp["analysis"] = analysis_info
                return resp, 201
            else:
                resp = err_resp(
                    "Something went wrong. Couldn't start the workflow",
                    "analysis_403",
                    403,
                )
                db.session.delete(new_analysis)
                db.session.commit()
                return resp, 403
        except Exception as error:
            if new_analysis:
                db.session.delete(new_analysis)
                db.session.commit()
                if storage_path:
                    rmtree(storage_path)
            logger.error(error)
            return internal_err_resp()

    @staticmethod
    def create_analysis(user_id, data):
        try:
            workflow_id = data.get("workflow_id", None)
            logger.info(f"Analysis uses the following workflow {workflow_id}")
            # workflows are assumed to be accessible by everyone here
            if not workflow_id or not (
                workflow := Workflow.query.filter_by(id=workflow_id).first()
            ):
                return err_resp("invalid workflow", "workflow_404", 404)

            # loading workflow file
            workflow_structure = f'{current_app.config["FALCOEYE_ASSETS"]}/workflows/{workflow_id}/structure.json'
            logger.info(f"Loading workflow structure from {workflow_structure}")
            wf_structure = load_workflow_structure(workflow_structure)
            # checking if short or long analysis
            inline = wf_structure.get("inline", False)

            logger.info(f"Running workflow {workflow.id}")
            return AnalysisService.create_analysis_(
                user_id, workflow.id, wf_structure, data, inline
            )

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

            storage_path = (
                f"{current_app.config['USER_ASSETS']}/{user_id}/analysis/{analysis_id}/"
            )

            logging.info(f"Deleting data from {storage_path}")
            if exists(storage_path):
                rmtree(storage_path)
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
            analysis_dir = analysis.results_path
            # list all meta.json files
            meta_files = [
                f
                for f in current_app.config["FS_OBJ"].ls(analysis_dir)
                if f.endswith("meta.json")
            ]
            # TODO: support multiple meta files handling in the frontend
            #if current_app.config["FS_OBJ"].isfile(f"{analysis_dir}/meta.json"):
            if len(meta_files) > 0:
                meta_files.sort(key=lambda x: current_app.config["FS_OBJ"].info(x)['mtime'], reverse=True)
                selected_meta = meta_files[0]
                with current_app.config["FS_OBJ"].open(selected_meta) as f:
                    data = f.read()
                return send_file(BytesIO(data), mimetype="application/json")
            else:
                return err_resp("no output yet", "analysis_204", 204)
        except Exception as error:
            logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_analysis_file_by_id(user_id, analysis_id, file_name, ext):
        """Get analysis file by ID"""
        if not (
            analysis := Analysis.query.filter_by(
                creator=user_id, id=analysis_id
            ).first()
        ):
            return err_resp("analysis not found", "analysis_404", 404)

        try:
            # analysis_dir = (
            #     f'{current_app.config["USER_ASSETS"]}/{user_id}/analysis/{analysis_id}'
            # )
            analysis_dir = analysis.results_path
            full_name = f"{analysis_dir}/{file_name}.{ext}"
            logging.info(f"checking if file exists {full_name}")
            if current_app.config["FS_OBJ"].isfile(full_name):
                if ext == "csv":
                    with current_app.config["FS_OBJ"].open(full_name) as f:
                        data = f.read()
                    return send_file(BytesIO(data), mimetype="application/csv")
                elif ext == "mp4":
                    if (
                        current_app.config["DEPLOYMENT"] == "local"
                        or current_app.config["DEPLOYMENT"] == "k8s"
                    ):
                        return f"{request.url_root}api/analysis/{analysis_id}/{user_id}/video/{file_name}.mp4"
                    else:
                        bucket = current_app.config["FS_BUCKET"]
                        blob_path = full_name.replace(bucket, "")
                        logging.info(
                            f"generating 15 minutes signed url for {bucket} {blob_path}"
                        )
                        url = generate_download_signed_url_v4(bucket, blob_path, 15)
                        return url
                elif ext == "jpg":
                    with current_app.config["FS_OBJ"].open(full_name) as f:
                        img = f.read()
                        return send_file(
                            BytesIO(img),
                            mimetype="image/jpg",
                        )
                elif ext == "json":
                    with current_app.config["FS_OBJ"].open(
                        os.path.relpath(f"{analysis_dir}/{file_name}.{ext}")
                    ) as f:
                        data = f.read()
                    return send_file(BytesIO(data), mimetype="application/json")
                else:
                    return err_resp("not implemented", "analysis_501", 501)

            else:
                return err_resp("no output yet", "analysis_425", 425)
        except Exception as error:
            logger.error(error)
            return internal_err_resp()

    @staticmethod
    def update_analysis_by_id(user_id, analysis_id, data):
        """Delete a analysis from DB by name and user id"""
        if not (user := User.query.filter_by(id=user_id).first()):
            return err_resp("user not found", "user_400", 400)

        logger.info(f"Is {user.id} admin?")
        logger.info(f"{user.has_permission(Permission.CHANGE_ANALYSIS_DATA)}")
        if user.has_permission(Permission.CHANGE_ANALYSIS_DATA):
            if not (analysis := Analysis.query.filter_by(id=analysis_id).first()):
                return err_resp(
                    "analysis not found",
                    "analysis_404",
                    404,
                )
        else:
            return err_resp("unauthorized", "role_401", 401)

        try:
            # TODO: other fields
            status = data.get("status", analysis.status)
            analysis.status = status
            db.session.flush()
            db.session.commit()

            resp = message(True, "analysis edited")
            analysis_data = load_analysis_data(analysis)
            resp["analysis"] = analysis_data
            return resp, 200

        except Exception as error:
            logger.error(error)
            return internal_err_resp()
