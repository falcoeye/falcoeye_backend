import datetime

from app import db
from app.dbmodels.registry import Registry


def get_status(registry_id):
    if not (registry_item := Registry.query.filter_by(id=registry_id).first()):
        return None
    return registry_item.status


def register(user_id, camera_id, media_type, capture_path=""):
    try:
        new_registry_item = Registry(
            user=user_id,
            media_type=media_type,
            camera_id=camera_id,
            status="STARTED",
            created_at=datetime.utcnow(),
            capture_path=capture_path,
        )

        db.session.add(new_registry_item)
        db.session.flush()
        db.session.commit()
        return new_registry_item
    except Exception as error:
        return None


def change_status(registry_id, new_status):

    if not (registry_item := Registry.query.filter_by(id=registry_id).first()):
        return None
    try:
        new_registry_item = Registry(
            user=registry_item.user,
            media_type=registry_item.media_type,
            camera_id=registry_item.camera_id,
            status=new_status,
            created_at=registry_item.created_at,
        )

        registry_item = new_registry_item
        db.session.flush()
        db.session.commit()
        return registry_item
    except Exception as error:
        return None
