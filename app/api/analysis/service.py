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
from app.utils import (
    err_resp,
    exists,
    generate_download_signed_url_v4,
    get_service,
    internal_err_resp,
    message,
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
    def get_analysis(user_id, orderby, per_page, page, order_dir):
        """Get a list of all user analysis"""
        if order_dir == "desc":
            orderby += "_desc"
        orderby = orderby_dict.get(orderby, Media.created_at)
        query = (
            Analysis.query.filter_by(creator=user_id)
            .order_by(orderby)
            .paginate(page, per_page=per_page)
        )
        if not (analysis := query.items):
            return err_resp("no analysis found", "analysis_404", 404)

        lastPage = not query.has_next
        try:
            analysis_data = load_analysis_data(analysis, many=True)
            if len(analysis_data) == 0:
                return err_resp("no analysis found", "analysis_404", 404)
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
                "analysis": {"id": str(new_analysis.id), "args": wf_args},
                "workflow": wf_structure,
            }
            workflow_service = get_service(
                "falcoeye-workflow"
            )  # current_app.config["WORKFLOW_HOST"]
            logger.info(
                f"Sending request to workflow server on {workflow_service}/api/analysis"
            )
            headers = {"accept": "application/json", "Content-Type": "application/json"}

            wf_resp = requests.post(
                f"{workflow_service}/api/analysis/", json=anal_data, headers=headers
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
            analysis_dir = (
                f'{current_app.config["USER_ASSETS"]}/{user_id}/analysis/{analysis_id}'
            )
            logging.info(f"checking if meta exists {analysis_dir}/meta.json")
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
            analysis_dir = (
                f'{current_app.config["USER_ASSETS"]}/{user_id}/analysis/{analysis_id}'
            )

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
                else:
                    return err_resp("not implemented", "analysis_501", 501)
            else:
                return err_resp("no output yet", "analysis_425", 425)
        except Exception as error:
            logger.error(error)
            return internal_err_resp()
