import logging
import shutil
from datetime import datetime

from flask import current_app

from app import db
from app.api import registry
from app.dbmodels.camera import Camera
from app.dbmodels.schemas import ImageSchema
from app.dbmodels.studio import Image as Image
from app.dbmodels.studio import Video as Video
from app.utils import err_resp, internal_err_resp, message

from .utils import load_image_data, load_video_data, mkdir


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
            # TODO: eliminate this somehow
            for v in video_data:
                v["media_type"] = "video"
            for i in image_data:
                v["media_type"] = "image"

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
        note = data.get("note", "")
        tags = data.get("tags", "")
        camera_id = data.get("camera_id", None)
        workflow_id = data.get("workflow_id", None)
        registry_key = data.get("registry_key", None)

        if not registry_key or not (
            registry_item := registry.get_registry(registry_key)
        ):
            return err_resp("Invalid registry key", "registry_404", 404)

        if registry_item.status == "FAILED":
            return err_resp("Registry item failed", "registry_404", 404)

        # TODO: camera id and workflow name, if any, should be part of the metadata of the image

        # user only send registry key here.
        try:
            new_image = Image(
                user=user_id,
                tags=tags,
                note=note,
                camera_id=camera_id,
                workflow_id=workflow_id,
                created_at=datetime.utcnow(),
            )
            db.session.add(new_image)
            db.session.flush()
            db.session.commit()

            imgs_dir = (
                f'{current_app.config["USER_ASSETS"]}/{user_id}/images/{new_image.id}/'
            )
            mkdir(imgs_dir)

            extension = registry_item.capture_path.split("/")[-1].split(".")[-1]
            try:
                shutil.move(
                    registry_item.capture_path, f"{imgs_dir}/img_original.{extension}"
                )
            except Exception as error:
                return err_resp("Failed to move item", "move_404", 404)

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
        note = data.get("note", "")
        tags = data.get("tags", "")
        camera_id = data.get("camera_id", None)
        workflow_id = data.get("workflow_id", None)
        registry_key = data.get("registry_key", None)

        logging.info(
            f"Creating new video item for {user_id} using registry {registry_key}"
        )
        if not registry_key or not (
            registry_item := registry.get_registry(registry_key)
        ):
            return err_resp("Invalid registry key", "registry_404", 404)

        if registry_item.status == "FAILED":
            return err_resp("Registry item failed", "registry_404", 404)

        try:
            new_video = Video(
                user=user_id,
                tags=tags,
                note=note,
                camera_id=camera_id,
                workflow_id=workflow_id,
                created_at=datetime.utcnow(),
            )
            db.session.add(new_video)
            db.session.flush()
            db.session.commit()

            video_dir = (
                f'{current_app.config["USER_ASSETS"]}/{user_id}/videos/{new_video.id}/'
            )
            logging.info(f"Creating user video directory {video_dir}")
            mkdir(video_dir)
            logging.info(f"Moving video from {registry_item.capture_path}")
            extension = registry_item.capture_path.split("/")[-1].split(".")[-1]
            try:
                shutil.move(
                    registry_item.capture_path,
                    f"{video_dir}/video_original.{extension}",
                )
            except Exception as error:
                return err_resp("Failed to move item", "move_404", 404)

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
