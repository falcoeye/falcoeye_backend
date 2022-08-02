import json
import os
from datetime import timedelta

import fsspec

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Change the secret key in production run.
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(24))
    DEBUG = False

    # JWT Extended config
    JWT_SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(24))

    JWT_HEADER_NAME = os.environ.get("JWT_HEADER_NAME", "X-API-KEY")
    JWT_HEADER_TYPE = os.environ.get("JWT_HEADER_TYPE", "JWT")

    # Set the token to expire every week
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # flask restx settings
    SWAGGER_UI_DOC_EXPANSION = "list"

    # Streamer config
    STREAMER_HOST = os.environ.get("STREAMER_HOST", "http://127.0.0.1:5000")
    WORKFLOW_HOST = os.environ.get("WORKFLOW_HOST", "http://127.0.0.1:7000")

    # admin
    FLASK_ADMIN = "FALCOEYE_STREAMING@falcoeye.ai"

    # file system interface
    FS_PROTOCOL = os.environ.get("FS_PROTOCOL", "file")
    FS_BUCKET = os.environ.get("FS_BUCKET", "")
    FS_PROJECT = os.environ.get("FS_PROJECT", "falcoeye")
    FS_TOKEN = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "cloud")
    if FS_TOKEN != "cloud":
        # running localy
        with open(FS_TOKEN) as f:
            FS_TOKEN = json.load(f)

    if FS_PROTOCOL in ("gs", "gcs"):
        import gcsfs

        FS_OBJ = gcsfs.GCSFileSystem(project=FS_PROJECT, token=FS_TOKEN)
        FS_IS_REMOTE = True

        TEMPORARY_DATA_PATH = os.environ.get(
            "TEMPORARY_DATA_PATH", f"{FS_BUCKET}/falcoeye-temp/data/"
        )
        FALCOEYE_ASSETS = os.environ.get(
            "FALCOEYE_ASSETS", f"{FS_BUCKET}/falcoeye-assets/"
        )
        USER_ASSETS = os.environ.get("USER_ASSETS", f"{FS_BUCKET}/user-assets")

    elif FS_PROTOCOL == "file":
        FS_OBJ = fsspec.filesystem(FS_PROTOCOL)
        FS_IS_REMOTE = False

        TEMPORARY_DATA_PATH = os.environ.get(
            "TEMPORARY_DATA_PATH", f"{basedir}/tests/falcoeye-temp/data/"
        )
        FALCOEYE_ASSETS = os.environ.get(
            "FALCOEYE_ASSETS", f"{basedir}/tests/falcoeye-assets/"
        )
        USER_ASSETS = os.environ.get("USER_ASSETS", f"{basedir}/tests/user-assets/")

    else:
        raise SystemError(f"support for {FS_PROTOCOL} has not been added yet")


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "data-dev.sqlite")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    # In-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "data.sqlite")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config_by_name = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig,
    default=DevelopmentConfig,
)
