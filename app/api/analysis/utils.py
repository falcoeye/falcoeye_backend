import json

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
    with open(structure_file) as f:
        structure = json.load(f)

    return structure
