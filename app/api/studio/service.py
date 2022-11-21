import logging
import os
from datetime import datetime

from flask import current_app, request, send_file
from sqlalchemy import desc

from app import db
from app.api import registry
from app.api.capture.streamer import Streamer
from app.dbmodels.studio import Image as Image
from app.dbmodels.studio import Media as Media
from app.dbmodels.studio import Video as Video
from app.utils import err_resp, exists, internal_err_resp, message, mkdir, move, rmtree

from .utils import load_image_data, load_media_data, load_video_data

logger = logging.getLogger(__name__)

orderby_dict = {
    "media_type": Media.media_type,
    "created_at": Media.created_at,
    "camera": Media.camera,
    "note": Media.note,
    "tags": Media.tags,
    "workflow": Media.workflow,
    "duration": Media.duration,
    "media_type_desc": desc(Media.media_type),
    "created_at_desc": desc(Media.created_at),
    "camera_desc": desc(Media.camera),
    "note_desc": desc(Media.note),
    "tags_desc": desc(Media.tags),
    "workflow_desc": desc(Media.workflow),
    "duration_desc": desc(Media.duration),
}


class StudioService:
    @staticmethod
    def get_user_media(user_id, orderby, per_page, page, order_dir):
        """Get user data by username"""
        if order_dir == "desc":
            orderby += "_desc"
        orderby = orderby_dict.get(orderby, Media.created_at)
        query = (
            Media.query.filter_by(user=user_id)
            .order_by(orderby)
            .paginate(page, per_page=per_page)
        )
        if not (media := query.items):
            resp = message(True, "media data sent")
            resp["media"] = []
            resp["lastPage"] = True
            return resp, 200

        lastPage = not query.has_next
        # images = Image.query.filter_by(user=user_id).all()
        # if not videos and not images:
        #    resp = message(True, "no media found")
        #    return resp, 204

        try:
            media_data = load_media_data(media, many=True)
            # video_data = load_video_data(videos, many=True)
            # image_data = load_image_data(images, many=True)
            # TODO: eliminate this somehow
            # for v in video_data:
            #     v["media_type"] = "video"
            # for i in image_data:
            #     i["media_type"] = "image"

            # media_data = video_data + image_data
            logger.info(f"Number of media: {len(media_data)}")
            resp = message(True, "media data sent")
            resp["media"] = media_data
            resp["lastPage"] = lastPage
            return resp, 200

        except Exception as error:
            logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_user_media_count(user_id):
        """Get user data by username"""
        media_count = Media.query.filter_by(user=user_id).count()
        try:
            resp = message(True, "media count data sent")
            resp["media_count"] = media_count
            return resp, 200
        except Exception as error:
            logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_image(user_id, media_id):

        if not (
            image := Media.query.filter_by(
                user=user_id, id=media_id, media_type="image"
            ).first()
        ):
            return err_resp("image not found", "image_404", 404)
        try:
            # TODO: Add image link
            image_data = load_image_data(image)
            resp = message(True, "image data sent")
            resp["image"] = image_data
            return resp, 200
        except Exception as error:
            logger.error(error)
            return internal_err_resp()

    @staticmethod
    def create_image(user_id, data):

        logger.info(f"Creating image for {user_id} data: {data}")
        note = data.get("note", "")
        tags = data.get("tags", "")
        camera_id = data.get("camera_id", None)
        workflow_id = data.get("workflow_id", None)
        registry_key = data.get("registry_key", None)

        if not registry_key or not (
            registry_item := registry.get_registry(registry_key)
        ):
            return err_resp("invalid registry key", "registry_403", 403)

        if registry_item.status == "FAILED":
            return message("process failed", "registry_417", 417)

        # user only send registry key here.
        try:
            new_image = Media(
                user=user_id,
                tags=tags,
                note=note,
                camera_id=camera_id,
                workflow_id=workflow_id,
                created_at=datetime.utcnow(),
                media_type="image",
            )
            db.session.add(new_image)
            db.session.flush()
            db.session.commit()

            registry_item.status = "PROCESSED"
            db.session.add(registry_item)
            db.session.flush()
            db.session.commit()

            logger.info("Image database object created")

            imgs_dir = (
                f'{current_app.config["USER_ASSETS"]}/{user_id}/images/{new_image.id}/'
            )
            mkdir(imgs_dir)

            logger.info(f"Moving image from {registry_item.capture_path} to {imgs_dir}")

            extension = registry_item.capture_path.split("/")[-1].split(".")[-1]
            try:
                move(registry_item.capture_path, f"{imgs_dir}/img_original.{extension}")
                for s in [75, 120, 260, 400]:
                    thumbnail_s = registry_item.capture_path.replace(
                        f".{extension}", f"_{s}.{extension}"
                    )
                    logging.info(f"Checking if {thumbnail_s} exists?")
                    if exists(thumbnail_s):
                        logger.info(
                            f"Moving thumbnail from {thumbnail_s} to {imgs_dir}/img_{s}.{extension}"
                        )
                        move(thumbnail_s, f"{imgs_dir}/img_{s}.{extension}")

            except Exception as error:
                return err_resp("process failed", "move_417", 417)

            img_info = load_image_data(new_image)
            resp = message(True, "image added")
            resp["image"] = img_info
            return resp, 201
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def delete_image(user_id, media_id):

        if (
            img := Media.query.filter_by(
                user=user_id, id=media_id, media_type="image"
            ).first()
        ) is None:
            return err_resp("image not found", "image_404", 404)
        try:
            db.session.delete(img)
            db.session.flush()
            db.session.commit()

            image_dir = (
                f'{current_app.config["USER_ASSETS"]}/{user_id}/images/{media_id}/'
            )
            if exists(image_dir):
                resp = message(True, "image deleted")
                return resp, 200
            try:
                logging.info(f"deleting {image_dir}")
                rmtree(image_dir)
                resp = message(True, "image deleted")
                return resp, 200
            except Exception as error:
                resp = message(True, "deletion partially failed")
                return resp, 417
        except Exception as error:
            logger.error(error)
            return internal_err_resp()

    @staticmethod
    def edit_image(user_id, media_id, data):
        if (
            media := Media.query.filter_by(
                user=user_id, id=media_id, media_type="image"
            ).first()
        ) is None:
            return err_resp("media not found", "media_404", 404)
        tags = data.get("tags", media.tags)
        note = data.get("note", media.note)
        try:
            media.tags = tags
            media.note = note
            db.session.flush()
            db.session.commit()
            resp = message(True, "media edited")
            media_data = load_image_data(media)
            resp["image"] = media_data
            return resp, 200
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def get_video(user_id, media_id):
        if not (
            video := Media.query.filter_by(
                user=user_id, id=media_id, media_type="video"
            ).first()
        ):
            return err_resp("video not found", "video_404", 404)
        try:
            video_data = load_video_data(video)
            resp = message(True, "video data sent")
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

        logger.info(
            f"Creating new video item for {user_id} using registry {registry_key}"
        )
        if not registry_key or not (
            registry_item := registry.get_registry(registry_key)
        ):
            return err_resp("invalid registry key", "registry_403", 403)

        if registry_item.status == "FAILED":
            return err_resp("process failed", "registry_417", 417)

        try:
            new_video = Media(
                user=user_id,
                tags=tags,
                note=note,
                camera_id=camera_id,
                workflow_id=workflow_id,
                created_at=datetime.utcnow(),
                media_type="video",
            )
            db.session.add(new_video)
            db.session.flush()
            db.session.commit()

            registry_item.status = "PROCESSED"
            db.session.add(registry_item)
            db.session.flush()
            db.session.commit()

            video_dir = (
                f'{current_app.config["USER_ASSETS"]}/{user_id}/videos/{new_video.id}/'
            )
            logger.info(f"Creating user video directory {video_dir}")
            mkdir(video_dir)
            extension = registry_item.capture_path.split("/")[-1].split(".")[-1]
            target_file = f"{video_dir}/video_original.{extension}"
            logger.info(
                f"Moving video from {registry_item.capture_path} to {target_file}"
            )
            try:
                move(
                    registry_item.capture_path,
                    target_file,
                )
                for s in [260]:
                    thmb_img = target_file.replace(
                        f"_original.{extension}", f"_{s}.jpg"
                    )
                    logging.info(
                        f"Generating thumbnail from {target_file} and store it in {thmb_img}"
                    )
                    try:
                        streamer_resp = Streamer.generate_thumbnail(
                            target_file, thmb_img
                        )
                    except Exception as e:
                        pass

                logger.info("Moving video succeeded")
            except Exception as error:
                return err_resp("process failed", "move_417", 417)

            video_info = load_video_data(new_video)
            resp = message(True, "video added")
            resp["video"] = video_info
            return resp, 201
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def delete_video(user_id, media_id):
        if (
            video := Media.query.filter_by(
                user=user_id, id=media_id, media_type="video"
            ).first()
        ) is None:
            return err_resp("video not found", "video_404", 404)
        try:
            db.session.delete(video)
            db.session.flush()
            db.session.commit()
            video_dir = (
                f'{current_app.config["USER_ASSETS"]}/{user_id}/videos/{media_id}/'
            )
            if not exists(video_dir):
                return message(True, "video deleted"), 200
            try:
                logging.info(f"deleting {video_dir}")
                rmtree(video_dir)
                resp = message(True, "video deleted")
                return resp, 200
            except Exception as error:
                resp = message(True, "deletion partially failed")
                return resp, 417
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def edit_video(user_id, media_id, data):
        if (
            media := Media.query.filter_by(
                user=user_id, id=media_id, media_type="video"
            ).first()
        ) is None:
            return err_resp("media not found", "media_404", 404)
        tags = data.get("tags", media.tags)
        note = data.get("note", media.note)
        try:
            media.tags = tags
            media.note = note
            db.session.flush()
            db.session.commit()
            resp = message(True, "media edited")
            media_data = load_video_data(media)
            resp["video"] = media_data
            return resp, 200
        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()
