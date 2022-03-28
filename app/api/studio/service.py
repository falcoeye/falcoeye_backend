from datetime import datetime

from flask import current_app

from app import db
from app.dbmodels.camera import Camera
from app.dbmodels.schemas import ImageSchema
from app.dbmodels.studio import Image as Image
from app.dbmodels.studio import Video as Video
from app.utils import err_resp, internal_err_resp, message

from .utils import load_image_data, load_video_data


class StudioService:
    @staticmethod
    def get_user_media(user_id):
        """Get user data by username"""
        videos = Video.query.filter_by(user=user_id).all()
        images = Image.query.filter_by(user=user_id).all()
        if not videos and not images:
            resp = message(True, "No media found!")
            return resp, 204

        try:
            video_data = load_video_data(videos, many=True)
            image_data = load_image_data(images, many=True)
            media_data = video_data + image_data

            resp = message(True, "User media sent")
            resp["media"] = media_data
            return resp, 200

        except Exception as error:
            raise
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_image(user_id, media_id):

        if not (image := Image.query.filter_by(user=user_id, id=media_id).first()):
            return err_resp("Image not found!", "image_404", 404)
        try:
            # TODO: Add image link
            image_data = load_image_data(image)
            resp = message(True, "Image data sent")
            resp["image"] = image_data
            return resp, 200
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def create_image(user_id, data):
        camera_id = data["camera_id"]
        note = data.get("note", "")
        tags = data.get("tags", "")
        workflow = data.get("workflow", None)
        if not (
            camera := Camera.query.filter_by(owner_id=user_id, id=camera_id).first()
        ):
            return err_resp("Camera is not registered", "invalid_camera", 403)

        try:
            new_image = Image(
                user=user_id,
                camera_id=camera.id,
                tags=tags,
                note=note,
                workflow=workflow,
            )
            db.session.add(new_image)
            db.session.flush()
            db.session.commit()

            img_info = load_image_data(new_image)
            resp = message(True, "Image has been added")
            resp["image"] = img_info
            return resp, 201
        except Exception as error:
            raise
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def delete_image(user_id, media_id):

        if (img := Image.query.filter_by(user=user_id, id=media_id).first()) is None:
            return err_resp("Image not found!", "image_404", 404)
        try:
            db.session.delete(img)
            db.session.flush()
            db.session.commit()

            resp = message(True, "Image deleted")

            return resp, 200
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_video(user_id, media_id):
        if not (video := Video.query.filter_by(user=user_id, id=media_id).first()):
            return err_resp("Video not found!", "video_404", 404)
        try:
            video_data = load_video_data(video)
            resp = message(True, "Video data sent")
            resp["video"] = video_data
            return resp, 200
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def create_video(user_id, data):
        camera_id = data["camera_id"]
        note = data.get("note", "")
        tags = data.get("tags", "")
        workflow = data.get("workflow", None)
        duration = data["duration"]

        try:
            new_video = Video(
                user=user_id,
                camera_id=camera_id,
                tags=tags,
                note=note,
                workflow=workflow,
            )
            db.session.add(new_video)
            db.session.flush()
            db.session.commit()

            video_info = load_video_data(new_video)
            resp = message(True, "Video has been added")
            resp["video"] = video_info
            return resp, 201
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def delete_video(user_id, media_id):
        if (video := Video.query.filter_by(user=user_id, id=media_id).first()) is None:
            return err_resp("Video not found!", "video_404", 404)
        try:
            db.session.delete(video)
            db.session.flush()
            db.session.commit()

            resp = message(True, "Video deleted")

            return resp, 200
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()
