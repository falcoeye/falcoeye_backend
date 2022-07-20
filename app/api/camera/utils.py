def load_camera_data(camera_db_obj, many=False):
    """Load camera's data
    Parameters:
    - Camera db object
    """
    from app.dbmodels.schemas import CameraSchema

    camera_schema = CameraSchema(many=many)
    data = camera_schema.dump(camera_db_obj)

    return data
