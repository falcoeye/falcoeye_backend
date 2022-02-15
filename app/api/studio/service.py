from datetime import datetime

from flask import current_app

from app import db
from app.dbmodels.schemas import ImageSchema
from app.dbmodels.studio import Image as Image
from app.dbmodels.studio import Video as Video
from app.utils import err_resp, internal_err_resp, message

from .utils import load_image_data, load_video_data


class StudioService:
    @staticmethod
    def get_user_media(user_id):
        """Get user data by username"""
        videos = Video.query.filter_by(user=user_id)
        images = Image.query.filter_by(user=user_id)

        try:
            video_data = [load_video_data(v, "short") for v in videos]
            image_data = [load_image_data(i, "short") for i in images]
            media_data = videos + image_data

            resp = message(True, "User data sent")
            resp["media"] = media_data
            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_image(user_id, media_id):
        try:
            image = Image.query.filter_by(user=user_id, id=media_id).first()
            image_data = load_image_data(image, "short")
            resp = message(True, "Image successfully retrieved.")
            resp["image"] = image_data
            return resp, 200
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def add_image(temprary_id, user_id, camera, note, tags, workflow):
        try:
            new_image = Image(
                user=user_id,
                camera=camera,
                tags=tags,
                note=note,
                workflow=workflow,
                creation_datetime=datetime.utcnow(),
            )

            db.session.add(new_image)
            db.session.flush()
            db.session.commit()

            img_info = load_image_data(new_image, "full")
            resp = message(True, "Image has been added.")
            resp["image"] = img_info
            return resp, 201
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def delete_image(user_id, media_id):
        # Check if the email is taken

        if (img := Image.query.filter_by(user=user_id, id=media_id).first()) is None:
            return err_resp("Image doesn't exist", "image_not_exist", 403)
        try:
            img_info = load_image_data(img)
            resp = message(True, "Image has been deleted.")
            resp["image"] = img_info

            db.session.delete(img)

            db.session.flush()
            db.session.commit()
            return resp, 201
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_video(user_id, media_id):
        try:
            video = Video.query.filter_by(user=user_id, id=media_id).first()
            video_data = load_video_data(video, "short")
            resp = message(True, "Video successfully retrieved.")
            resp["video"] = video_data
            return resp, 200
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def add_video(temprary_id, user_id, camera, note, tags, duration, workflow):
        try:
            video = Video(
                user=user_id,
                camera=camera,
                tags=tags,
                note=note,
                workflow=workflow,
                creation_datetime=datetime.utcnow(),
                duration=duration,
            )

            db.session.add(video)
            db.session.flush()
            db.session.commit()

            vid_infor = load_image_data(video, "full")
            resp = message(True, "Video has been added.")
            resp["video"] = vid_infor
            return resp, 201
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def delete_video(user_id, media_id):
        # Check if the email is taken

        if (vid := Video.query.filter_by(user=user_id, id=media_id).first()) is None:
            return err_resp("Video doesn't exist", "video_not_exist", 403)
        try:
            vid_info = load_video_data(vid)
            resp = message(True, "Video has been deleted.")
            resp["video"] = vid_info

            db.session.delete(vid)

            db.session.flush()
            db.session.commit()
            return resp, 201
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()
