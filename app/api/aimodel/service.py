import logging
from datetime import datetime

from flask import current_app

from app import db
from app.dbmodels.ai import AIModel, Dataset
from app.dbmodels.schemas import AIModelSchema
from app.utils import err_resp, internal_err_resp, message

from .utils import load_aimodel_data

aimodel_schema = AIModelSchema()


class AIModelService:
    @staticmethod
    def get_aimodels():
        """Get a list of all aimodels"""
        if not (aimodels := AIModel.query.all()):
            return err_resp("no aimodel found", "aimodel_404", 404)

        try:
            aimodel_data = load_aimodel_data(aimodels, many=True)
            resp = message(True, "aimodel data sent")
            resp["aimodel"] = aimodel_data

            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def create_aimodel(user_id, data):
        try:
            name = data["name"]
            if AIModel.query.filter_by(name=name).first() is not None:
                return err_resp("aimodel name already exists", "name_taken", 403)

            dataset_name = data.get("dataset", "")

            if dataset_name:
                if not (dataset := Dataset.query.filter_by(name=dataset_name).first()):
                    logging.warning("dataset is not in the database")
                    dataset_id = dataset.id
            else:
                dataset_name = ""
                dataset_id = None

            new_aimodel = AIModel(
                name=name,
                creator=user_id,
                publish_date=datetime.utcnow(),
                architecture=data["architecture"],
                backbone=data["backbone"],
                dataset_id=dataset_id,
                technology=data["technology"],
                speed=data["speed"],
            )

            db.session.add(new_aimodel)
            db.session.flush()
            db.session.commit()

            aimodel_info = aimodel_schema.dump(new_aimodel)
            resp = message(True, "aimodel added")
            resp["aimodel"] = aimodel_info
            return resp, 201
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_aimodel_by_id(aimodel_id):
        """Get aimodel by ID"""
        if not (aimodel := AIModel.query.filter_by(id=aimodel_id).first()):
            return err_resp("aimodel not found", "aimodel_404", 404)

        try:
            aimodel_data = load_aimodel_data(aimodel)
            resp = message(True, "aimodel data sent")
            resp["aimodel"] = aimodel_data

            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def delete_aimodel(user_id, aimodel_id):
        """Delete a aimodel from DB by name and user id"""
        if not (
            aimodel := AIModel.query.filter_by(creator=user_id, id=aimodel_id).first()
        ):
            return err_resp(
                "aimodel not found",
                "aimodel_404",
                404,
            )

        try:
            db.session.delete(aimodel)
            db.session.commit()

            resp = message(True, "aimodel deleted")
            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()
