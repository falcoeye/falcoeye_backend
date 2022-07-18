import os.path
import shutil

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
    path = os.path.relpath(path)
    if current_app.config["FS_OBJ"].isdir(path):
        return
    if current_app.config["FS_IS_REMOTE"]:
        if not path.endswith("/"):
            path = path + "/"
        current_app.config["FS_OBJ"].touch(path)
    else:
        current_app.config["FS_OBJ"].makedirs(path)


def rmtree(path):
    path = os.path.relpath(path)
    if not path.endswith("/"):
        path = path + "/"
    if not current_app.config["FS_OBJ"].isdir(path):
        return
    if current_app.config["FS_IS_REMOTE"]:
        current_app.config["FS_OBJ"].delete(path, recursive=True)
    else:
        shutil.rmtree(path)


def move(src, dst):
    src = os.path.relpath(src)
    dst = os.path.relpath(dst)

    if current_app.config["FS_IS_REMOTE"]:
        current_app.config["FS_OBJ"].move(src, dst)
    else:
        shutil.move(src, dst)


def put(f_from, f_to):
    f_from = os.path.relpath(f_from)
    f_to = os.path.relpath(f_to)

    if current_app.config["FS_IS_REMOTE"]:
        current_app.config["FS_OBJ"].put(f_from, f_to)
    else:
        shutil.copy2(f_from, f_to)
