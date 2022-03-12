from datetime import datetime

from flask import current_app

from app import db
from app.dbmodels.ai import Analysis
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
            resp = message(True, "analysis data sent")
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
                return err_resp("Name is already being used.", "name_taken", 403)
            new_analysis = Analysis(
                name=data["name"],
                creator=user_id,
                publish_date=datetime.utcnow(),
                analysis_id=data["analysis_id"],
                usedfor=data["usedfor"],
                consideration=data["consideration"],
                assumption=data["assumption"],
                accepted_media=data["accepted_media"],
                results_type=data["results_type"],
                thumbnail_url=data["thumbnail_url"],
            )
            db.session.add(new_analysis)
            db.session.flush()
            db.session.commit()

            analysis_info = analysis_schema.dump(new_analysis)
            resp = message(True, "Analysis has been added.")
            resp["analysis"] = analysis_info
            return resp, 201
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_analysis_by_id(analysis_id):
        """Get analysis by ID"""
        if not (analysis := Analysis.query.filter_by(id=analysis_id).first()):
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
                owner_id=user_id, id=analysis_id
            ).first()
        ):
            return err_resp(
                "Analysis not found or belongs to a different owner",
                "analysis_404",
                404,
            )

        try:
            db.session.delete(analysis)
            db.session.commit()

            resp = message(True, "analysis deleted")
            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()
