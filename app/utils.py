from flask import current_app


def message(status, message):
    response_object = {"status": status, "message": message}
    return response_object


def validation_error(status, errors):
    response_object = {"status": status, "errors": errors}

    return response_object


def err_resp(msg, reason, code):
    err = message(False, msg)
    err["error_reason"] = reason
    return err, code


def internal_err_resp():
    err = message(False, "Something went wrong during the process!")
    err["error_reason"] = "server_error"
    return err, 500


def mkdir(path):
    if current_app.config["FS_OBJ"].isdir(path):
        return
    if current_app.config["FS_IS_REMOTE"]:
        current_app.config["FS_OBJ"].touch(path)
    else:
        current_app.config["FS_OBJ"].makedirs(path)
