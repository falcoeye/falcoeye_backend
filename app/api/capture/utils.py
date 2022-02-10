import os


def load_video_data(video_db_obj, level="full"):
    """Load short video's data

    Parameters:
    - Video db object
    - level: short | full
    """
    if level == "short":
        from app.dbmodels.schemas import VideoSchemaShort

        video_schema = VideoSchemaShort()
    elif level == "full":
        from app.dbmodels.schemas import VideoSchema

        video_schema = VideoSchema()

    data = video_schema.dump(video_db_obj)
    return data


def load_image_data(video_db_obj, level="full"):
    """Load short video's data

    Parameters:
    - Video db object
    - level: short | full
    """
    if level == "short":
        from app.dbmodels.schemas import ImageSchemaShort

        image_schema = ImageSchemaShort()
    elif level == "full":
        from app.dbmodels.schemas import ImageSchema

        image_schema = ImageSchema()

    data = image_schema.dump(video_db_obj)
    return data


def mkdir(path):
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
