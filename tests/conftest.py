"""Global pytest fixtures."""
import pytest

from app import create_app
from app import db as database
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
def harbourcamera(db, user, manufacturer, streamer):
    harbourcamera = Camera(
        name="Harbour Village Bonaire Coral Reef",
        status="RUNNING",
        manufacturer_id=manufacturer.id,
        streamer_id=streamer.id,
        owner_id=user.id,
        url="https://www.youtube.com/watch?v=tk-qJJbdOh4",
    )
    db.session.add(harbourcamera)
    db.session.commit()
    return harbourcamera


@pytest.fixture
def image(db, user, harbourcamera):

    image = Image(
        user=user.id, camera_id=harbourcamera.id, tags="DummyTags", note="DummyNote"
    )
    db.session.add(image)
    db.session.commit()
    return image


@pytest.fixture
def video(db, user, harbourcamera):

    video = Video(
        user=user.id,
        camera_id=harbourcamera.id,
        tags="DummyTags",
        note="DummyNote",
        duration=10,
    )
    db.session.add(video)
    db.session.commit()
    return video
