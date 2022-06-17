from datetime import datetime

from app import db
from app.dbmodels.registry import Registry


def get_status(registry_id):
    if not (registry_item := Registry.query.filter_by(id=registry_id).first()):
        return None
    return registry_item.status


def register(user_id, camera_id, media_type, prefix):
    try:

        new_registry_item = Registry(
            user=user_id,
            media_type=media_type,
            camera_id=camera_id,
            status="STARTED",
            created_at=datetime.utcnow(),
        )
        db.session.add(new_registry_item)
        db.session.flush()
        db.session.commit()
        if media_type == "image":
            capture_path = f"{prefix}/{new_registry_item.id}.jpg"
        elif media_type == "video":
            capture_path = f"{prefix}/{new_registry_item.id}.mp4"

        new_registry_item.capture_path = capture_path
        db.session.add(new_registry_item)
        db.session.flush()
        db.session.commit()

        return new_registry_item
    except Exception as error:
        raise
        return None


def change_status(registry_id, new_status):

    if not (registry_item := Registry.query.filter_by(id=registry_id).first()):
        return None
    try:
        registry_item.status = new_status
        db.session.flush()
        db.session.commit()
        return registry_item
    except Exception as error:
        return None
