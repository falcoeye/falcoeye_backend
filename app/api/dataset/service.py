from datetime import datetime

from flask import current_app

from app import db
from app.dbmodels.ai import Dataset
from app.dbmodels.schemas import DatasetSchema
from app.utils import err_resp, internal_err_resp, message

from .utils import load_dataset_data

dataset_schema = DatasetSchema()


class DatasetService:
    @staticmethod
    def get_datasets():
        """Get a list of all datasets"""
        if not (datasets := Dataset.query.all()):
            return err_resp("no datasets found", "dataset_404", 404)

        try:
            dataset_data = load_dataset_data(datasets, many=True)
            resp = message(True, "dataset data sent")
            resp["dataset"] = dataset_data

            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def create_dataset(user_id, data):
        try:
            name = data["name"]
            if Dataset.query.filter_by(name=name).first() is not None:
                return err_resp("name already exists", "name_taken", 403)
            new_dataset = Dataset(
                name=data["name"],
                creator=user_id,
                annotation_type=data["annotation_type"],
                image_width=data["image_width"],
                image_height=data["image_height"],
                size_type=data["size_type"],
            )
            db.session.add(new_dataset)
            db.session.flush()
            db.session.commit()

            dataset_info = dataset_schema.dump(new_dataset)
            resp = message(True, "dataset added")
            resp["dataset"] = dataset_info
            return resp, 201
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def delete_dataset(user_id, dataset_id):
        """Delete a dataset from DB by name and user id"""
        if not (
            dataset := Dataset.query.filter_by(creator=user_id, id=dataset_id).first()
        ):
            return err_resp(
                "dataset not found",
                "dataset_404",
                404,
            )

        try:
            db.session.delete(dataset)
            db.session.commit()

            resp = message(True, "dataset deleted")
            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_dataset_by_id(dataset_id):
        """Get dataset by ID"""
        if not (dataset := Dataset.query.filter_by(id=dataset_id).first()):
            return err_resp("dataset not found", "dataset_404", 404)

        try:
            dataset_data = load_dataset_data(dataset)
            resp = message(True, "dataset data sent")
            resp["dataset"] = dataset_data

            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()
