import json
import os

from flask import current_app


def load_registry_data(registry_db_obj, many=False):
    """Load registry's data

    Parameters:
    - Registry db object
    """
    from app.dbmodels.schemas import RegistrySchema

    registry_schema = RegistrySchema(many=many)
    data = registry_schema.dump(registry_db_obj)

    return data
