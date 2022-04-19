"""Global pytest fixtures."""
import datetime

import pytest

from app import create_app
from app import db as database
from app.dbmodels.ai import AIModel, Analysis, Dataset, Workflow
from app.dbmodels.camera import Camera, CameraManufacturer, Streamer
from app.dbmodels.studio import Image, Video
from app.dbmodels.user import Role, User

from .utils import EMAIL, PASSWORD, USERNAME


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
    user = User(email=EMAIL, password=PASSWORD, username=USERNAME)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def manufacturer(db):
    manufacturer = CameraManufacturer(name="DummyMaker")
    db.session.add(manufacturer)
    db.session.commit()
    return manufacturer


@pytest.fixture
def streamer(db):
    streamer = Streamer(name="youtube")
    db.session.add(streamer)
    db.session.commit()
    return streamer


@pytest.fixture
def camera(db, user, manufacturer, streamer):
    camera = Camera(
        name="DummyCamera",
        status="RUNNING",
        manufacturer_id=manufacturer.id,
        streamer_id=streamer.id,
        owner_id=user.id,
        url="https://test.test.com",
    )
    db.session.add(camera)
    db.session.commit()
    return camera


@pytest.fixture
def harbour_camera(db, user, manufacturer, streamer):
    harbour_camera = Camera(
        name="Harbour Village Bonaire Coral Reef",
        status="RUNNING",
        manufacturer_id=manufacturer.id,
        streamer_id=streamer.id,
        owner_id=user.id,
        url="https://www.youtube.com/watch?v=tk-qJJbdOh4",
    )
    db.session.add(harbour_camera)
    db.session.commit()
    return harbour_camera


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
        publish_date=datetime.datetime.now(),
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
        publish_date=datetime.datetime.now(),
        aimodel_id=aimodel.id,
        structure_file="/path/to/workflow.json",
        usedfor="detecting stuff",
        consideration="be careful",
        assumption="barely works",
        accepted_media="Video|Camera",
        results_description="stuff",
        results_type="csv",
        thumbnail_url="/path/to/thumbnail.jpg",
    )
    db.session.add(workflow)
    db.session.commit()
    return workflow


@pytest.fixture
def analysis(db, user, workflow):
    analysis = Analysis(
        name="analysis",
        creator=user.id,
        workflow_id=workflow.id,
        status="completed",
        results_path="/path/to/results",
    )
    db.session.add(analysis)
    db.session.commit()
    return analysis
