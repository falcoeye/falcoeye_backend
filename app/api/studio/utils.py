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


def load_media_data(media_db_obj, many=False):
    """Load short media's data

    Parameters:
    - Media db object
    - many:
    """

    from app.dbmodels.schemas import MediaSchema

    media_schema = MediaSchema(many=many)
    data = media_schema.dump(media_db_obj)
    return data
