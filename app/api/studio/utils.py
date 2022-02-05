

def load_video_short_data(video_db_obj):
    """Load short video's data

    Parameters:
    - Video db object
    """
    from app.dbmodels.schemas import VideoSchemaShort

    video_schema = VideoSchemaShort()

    data = video_schema.dump(video_db_obj)

    return data

def load_image_short_data(image_db_obj):
    """Load short video's data

    Parameters:
    - Image db object
    """
    from app.dbmodels.schemas import ImageSchemaShort

    image_schema = ImageSchemaShort()

    data = image_schema.dump(image_db_obj)

    return data
