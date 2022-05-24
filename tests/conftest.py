"""Global pytest fixtures."""
import os
from datetime import datetime

import pytest

from app import create_app
from app import db as database
from app.dbmodels.ai import AIModel, Analysis, Dataset, Workflow
from app.dbmodels.camera import Camera, CameraManufacturer
from app.dbmodels.registry import Registry
from app.dbmodels.studio import Image, Video
from app.dbmodels.user import Role, User

from .utils import EMAIL, PASSWORD, USERNAME

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
def manufacturer(db):
    manufacturer = CameraManufacturer(name="DummyMaker")
    db.session.add(manufacturer)
    db.session.commit()
    return manufacturer


@pytest.fixture
def camera(db, user, manufacturer):
    camera = Camera(
        name="DummyCamera",
        status="RUNNING",
        manufacturer_id=manufacturer.id,
        streaming_type="StreamingServer",
        owner_id=user.id,
        url="https://test.test.com",
    )
    db.session.add(camera)
    db.session.commit()
    return camera


@pytest.fixture
def harbour_camera(db, user, manufacturer):
    harbour_camera = Camera(
        name="Harbour Village Bonaire Coral Reef",
        status="RUNNING",
        manufacturer_id=manufacturer.id,
        streaming_type="StreamingServer",
        owner_id=user.id,
        url="https://www.youtube.com/watch?v=tk-qJJbdOh4",
    )
    db.session.add(harbour_camera)
    db.session.commit()
    return harbour_camera


@pytest.fixture
def registry_image(db, user, camera):
    registry = Registry(
        camera_id=str(camera.id),
        user=str(user.id),
        media_type="image",
        status="STARTED",
        capture_path="",
    )
    db.session.add(registry)
    db.session.commit()
    return registry


@pytest.fixture
def registry_video(db, user, camera):
    registry = Registry(
        camera_id=str(camera.id),
        user=str(user.id),
        media_type="video",
        status="STARTED",
        capture_path="",
    )
    db.session.add(registry)
    db.session.commit()
    return registry


@pytest.fixture
def image(db, user, harbour_camera):

    image = Image(
        user=user.id, camera_id=harbour_camera.id, tags="DummyTags", note="DummyNote"
    )
    db.session.add(image)
    db.session.commit()
    return image


@pytest.fixture
def video(db, user, harbour_camera):
    video = Video(
        user=user.id,
        camera_id=harbour_camera.id,
        tags="DummyTags",
        note="DummyNote",
        duration=10,
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
def workflow(db, user, aimodel):
    workflow = Workflow(
        name="FishCounter",
        creator=user.id,
        publish_date=datetime.now(),
        aimodel_id=aimodel.id,
        structure_file=f"{basedir}/../../falcoeye_workflow/workflows/kaust_fish_counter_threaded_async.json",
        usedfor="detecting stuff",
        consideration="be careful",
        assumption="barely works",
        results_description="stuff",
        thumbnail_url="/path/to/thumbnail.jpg",
    )
    db.session.add(workflow)
    db.session.commit()
    return workflow


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
