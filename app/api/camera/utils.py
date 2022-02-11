def load_camera_data(camera_db_obj):
    """Load camera's data

    Parameters:
    - Camera db object
    """
    from app.dbmodels.schemas import CameraSchema

    camera_schema = CameraSchema()

    data = camera_schema.dump(camera_db_obj)

    return data


def load_manufacturer_data(manufacturer_db_obj):
    """Load camera manufacturer's data

    Parameters:
    - Camera manufacturer db object
    """
    from app.dbmodels.schemas import CameraManufacturerSchema

    camera_manufacturer_schema = CameraManufacturerSchema()

    data = camera_manufacturer_schema.dump(manufacturer_db_obj)

    return data
