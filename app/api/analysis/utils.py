import json
import os

from flask import current_app


def load_analysis_data(analysis_db_obj, many=False):
    """Load analysis's data

    Parameters:
    - Analysis db object
    """
    from app.dbmodels.schemas import AnalysisSchema

    analysis_schema = AnalysisSchema(many=many)
    data = analysis_schema.dump(analysis_db_obj)

    return data


def load_workflow_structure(structure_file):
    with current_app.config["FS_OBJ"].open(os.path.relpath(structure_file)) as f:
        data = f.read()
    structure = json.loads(data.decode("utf-8"))

    return structure
