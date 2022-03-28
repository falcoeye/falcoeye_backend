def load_dataset_data(dataset_db_obj, many=False):
    """Load dataset's data

    Parameters:
    - Dataset db object
    """
    from app.dbmodels.schemas import DatasetSchema

    dataset_schema = DatasetSchema(many=many)
    data = dataset_schema.dump(dataset_db_obj)

    return data
