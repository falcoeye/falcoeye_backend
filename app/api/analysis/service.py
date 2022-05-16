from datetime import datetime

from flask import current_app

from app import db
from app.dbmodels.ai import Analysis
from app.dbmodels.ai import Workflow as Workflow
from app.dbmodels.schemas import AnalysisSchema
from app.utils import err_resp, internal_err_resp, message

from .utils import load_analysis_data

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

            name = data["name"]
            if Analysis.query.filter_by(name=name).first() is not None:
                return err_resp("Invalid data.", "name_403", 403)

            workflow_id = data.get("workflow_id", None)
            if not workflow_id:
                return err_resp("Invalid data.", "workflow_403", 403)

            # workflows are assumed to be accessable by everyone here
            if not (workflow := Workflow.query.filter_by(id=workflow_id).first()):
                return err_resp("Invalid data.", "workflow_404", 404)

            new_analysis = Analysis(
                name=name,
                creator=user_id,
                creation_date=datetime.utcnow(),
                status="new",
                workflow_id=workflow.id,
            )

            db.session.add(new_analysis)
            db.session.flush()
            db.session.commit()

            # TODO: send to workflow microservice here

            analysis_info = analysis_schema.dump(new_analysis)
            resp = message(True, "Analysis has been added.")
            resp["analysis"] = analysis_info
            return resp, 201
        except Exception as error:
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
