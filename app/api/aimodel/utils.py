def load_aimodel_data(aimodel_db_obj, many=False):
    """Load aimodel's data

    Parameters:
    - AI Model db object
    """
    from app.dbmodels.schemas import AIModelSchema

    aimodel_schema = AIModelSchema(many=many)
    data = aimodel_schema.dump(aimodel_db_obj)

    return data
