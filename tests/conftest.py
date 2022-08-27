"""Global pytest fixtures."""
import json
import logging
import os
from datetime import datetime

import pytest
from flask import current_app

from app import create_app
from app import db as database
from app.dbmodels.ai import AIModel, Analysis, Dataset, Workflow
from app.dbmodels.camera import Camera
from app.dbmodels.registry import Registry
from app.dbmodels.studio import Image, Media, Video
from app.dbmodels.user import Role, User
from app.utils import mkdir, put

from .utils import EMAIL, PASSWORD, USERNAME

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
basedir = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def app():
    app = create_app("testing")
    app.testing = True
    return app


@pytest.fixture
def client(app):
    with app.app_context():
        with app.test_client() as client:
            yield client


@pytest.fixture
def db(app, client, request):
    database.drop_all()
    database.create_all()
    database.session.commit()

    def fin():
        database.session.remove()

    request.addfinalizer(fin)
    return database


@pytest.fixture
def user(db):
    Role.insert_roles()
    user = User(email=EMAIL, password=PASSWORD, username=USERNAME)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def streaming_admin(db):
    a = {
        "email": "FALCOEYE_STREAMING@falcoeye.ai",
        "password": "FALCOEYE_STREAMING_PASS",
        "username": "FALCOEYE_STREAMING",
        "name": "FALCOEYE STREAMING",
    }
    Role.insert_roles()
    role = Role.query.filter_by(name="Admin").first()
    user = User(
        email=a["email"],
        password=a["password"],
        username=a["username"],
        name=a["name"],
        role_id=role.id,
    )
    db.session.add(user)
    db.session.commit()
    return a


@pytest.fixture
def camera(db, user):  # manufacturer):
    camera = Camera(
        name="DummyCamera",
        status="RUNNING",
        #       manufacturer_id=manufacturer.id,
        streaming_type="StreamingServer",
        owner_id=user.id,
        url="https://test.test.com",
    )
    db.session.add(camera)
    db.session.commit()
    return camera


@pytest.fixture
def harbour_camera(db, user):  # , manufacturer):
    harbour_camera = Camera(
        name="Harbour Village Bonaire Coral Reef",
        status="RUNNING",
        #        manufacturer_id=manufacturer.id,
        streaming_type="StreamingServer",
        owner_id=user.id,
        url="https://www.youtube.com/watch?v=tk-qJJbdOh4",
    )
    db.session.add(harbour_camera)
    db.session.commit()
    return harbour_camera


@pytest.fixture
def registry_image(app, db, user, camera):
    registry = Registry(
        camera_id=str(camera.id),
        user=str(user.id),
        media_type="image",
        status="STARTED",
        capture_path="",
    )
    db.session.add(registry)
    db.session.commit()

    user_img_dir = f"{app.config['TEMPORARY_DATA_PATH']}/{str(user.id)}/images/"
    logging.info(f"User temp image directory: {user_img_dir}")
    mkdir(user_img_dir)
    logging.info(f"Directory created? {os.path.exists(user_img_dir)}")

    img_filename = f"{user_img_dir}/{registry.id}.jpg"
    logging.info(f"Copying: {basedir}/media/fish.jpg to {img_filename}")
    put(f"{basedir}/media/fish.jpg", img_filename)

    registry.capture_path = img_filename
    db.session.add(registry)
    db.session.flush()
    db.session.commit()

    return registry


@pytest.fixture
def registry_video(app, db, user, camera):
    registry = Registry(
        camera_id=str(camera.id),
        user=str(user.id),
        media_type="video",
        status="STARTED",
        capture_path="",
    )
    db.session.add(registry)
    db.session.commit()

    user_videos_dir = f"{app.config['TEMPORARY_DATA_PATH']}/{str(user.id)}/videos/"
    logging.info(f"User temp video directory: {user_videos_dir}")
    mkdir(user_videos_dir)
    logging.info(f"Directory created? {os.path.exists(user_videos_dir)}")

    # Only mp4 is supported
    video_filename = f"{user_videos_dir}/{registry.id}.mp4"
    logging.info(
        f"Copying: {basedir}/media/arabian_angelfish_short.mp4 to {video_filename}"
    )
    put(f"{basedir}/media/arabian_angelfish_short.mp4", video_filename)

    registry.capture_path = video_filename
    db.session.add(registry)
    db.session.flush()
    db.session.commit()

    return registry


@pytest.fixture
def image(db, user, harbour_camera):

    image = Media(
        user=user.id,
        camera_id=harbour_camera.id,
        tags="DummyTags",
        note="DummyNote",
        media_type="image",
    )
    db.session.add(image)
    db.session.commit()
    return image


@pytest.fixture
def video(db, user, harbour_camera):
    video = Media(
        user=user.id,
        camera_id=harbour_camera.id,
        tags="DummyTags",
        note="DummyNote",
        duration=10,
        media_type="video",
    )
    db.session.add(video)
    db.session.commit()
    return video


@pytest.fixture
def dataset(db, user):
    dataset = Dataset(
        name="DummyDataset",
        creator=str(user.id),
        annotation_type="DummyType",
        image_width=1920,
        image_height=1080,
        size_type="DummySizeType",
    )

    db.session.add(dataset)
    db.session.commit()
    return dataset


@pytest.fixture
def aimodel(db, user, dataset):

    model = AIModel(
        name="FourtyThreeFish",
        creator=user.id,
        publish_date=datetime.now(),
        architecture="frcnn",
        backbone="resnet50",
        dataset_id=dataset.id,
        technology="tensorflow",
        speed=1,
    )
    db.session.add(model)
    db.session.commit()
    return model


@pytest.fixture
def workflow(app, db, user, aimodel):
    with open(
        f"{basedir}/../initialization/workflows/kaust_fish_counter_threaded_async.json"
    ) as f:
        workflow_json = json.load(f)

    workflow = Workflow(
        name="FishCounter",
        creator=user.id,
        publish_date=datetime.now(),
        aimodel_id=aimodel.id,
        usedfor="detecting stuff",
        consideration="be careful",
        assumption="barely works",
        results_description="stuff",
    )
    db.session.add(workflow)
    db.session.commit()

    workflow_dir = f'{app.config["FALCOEYE_ASSETS"]}/workflows/{workflow.id}/'
    logging.info(f"Creating workflow directory {workflow_dir}")

    mkdir(workflow_dir)
    logging.info("Writing structure file")
    with current_app.config["FS_OBJ"].open(
        os.path.relpath(f"{workflow_dir}/structure.json"), "w"
    ) as f:
        f.write(json.dumps(workflow_json["structure"]))

    return workflow


@pytest.fixture
def two_workflow(app, db, user, aimodel):
    with open(
        f"{basedir}/../initialization/workflows/kaust_fish_counter_threaded_async.json"
    ) as f:
        workflow_json = json.load(f)

    workflow1 = Workflow(
        name="FishCounter",
        creator=user.id,
        publish_date=datetime.now(),
        aimodel_id=aimodel.id,
        usedfor="detecting stuff",
        consideration="be careful",
        assumption="barely works",
        results_description="stuff",
    )
    workflow2 = Workflow(
        name="FishCounter2",
        creator=user.id,
        publish_date=datetime.now(),
        aimodel_id=aimodel.id,
        usedfor="detecting stuff",
        consideration="be careful",
        assumption="barely works",
        results_description="stuff",
    )
    db.session.add(workflow1)
    db.session.add(workflow2)
    db.session.commit()

    workflow_dir = f'{app.config["FALCOEYE_ASSETS"]}/workflows/{workflow1.id}/'
    logging.info(f"Creating workflow directory {workflow_dir}")

    mkdir(workflow_dir)
    logging.info("Writing structure file")
    with current_app.config["FS_OBJ"].open(
        os.path.relpath(f"{workflow_dir}/structure.json"), "w"
    ) as f:
        f.write(json.dumps(workflow_json["structure"]))

    return workflow1, workflow2


@pytest.fixture
def analysis(db, user, workflow):
    analysis = Analysis(
        name="analysis",
        creator=str(user.id),
        workflow_id=str(workflow.id),
        status="completed",
        results_path="/path/to/results",
        message="",
        created_at=datetime.utcnow(),
    )
    db.session.add(analysis)
    db.session.commit()
    return analysis


@pytest.fixture
def two_analysis(db, user, workflow):
    analysis1 = Analysis(
        name="analysis1",
        creator=str(user.id),
        workflow_id=str(workflow.id),
        status="completed",
        results_path="/path/to/results",
        message="",
        created_at=datetime.utcnow(),
    )
    analysis2 = Analysis(
        name="analysis2",
        creator=str(user.id),
        workflow_id=str(workflow.id),
        status="completed",
        results_path="/path/to/results",
        message="",
        created_at=datetime.utcnow(),
    )
    db.session.add(analysis1)
    db.session.add(analysis2)
    db.session.commit()
    return analysis1, analysis2
