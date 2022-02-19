def load_workflow_data(workflow_db_obj, many=False):
    """Load workflow's data

    Parameters:
    - Worlflow db object
    """
    from app.dbmodels.schemas import WorkflowSchema

    workflow_schema = WorkflowSchema(many=many)
    data = workflow_schema.dump(workflow_db_obj)

    return data
