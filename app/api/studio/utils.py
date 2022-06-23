import os


def mkdir(path):
    if os.path.exists(path):
        return
    os.makedirs(path)


def load_video_data(video_db_obj, many=False):
    """Load short video's data

    Parameters:
    - Video db object
    - many:
    """
    from app.dbmodels.schemas import VideoSchema

    video_schema = VideoSchema(many=many)
    data = video_schema.dump(video_db_obj)
    return data


def load_image_data(video_db_obj, many=False):
    """Load short video's data

    Parameters:
    - Video db object
    - many:
    """

    from app.dbmodels.schemas import ImageSchema

    image_schema = ImageSchema(many=many)
    data = image_schema.dump(video_db_obj)
    return data
