"""Global pytest fixtures."""
import pytest

from app import create_app
from app import db as database
from app.dbmodels.camera import Camera, CameraManufacturer
from app.dbmodels.user import User

from .utils import EMAIL, PASSWORD, USERNAME


@pytest.fixture
def app():
    app = create_app("testing")
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
def camera(db, user, manufacturer):
    camera = Camera(
        name="DummyCamera",
        status="RUNNING",
        manufacturer_id=manufacturer.id,
        owner_id=user.id,
        url="https://test.test.com",
    )
    db.session.add(camera)
    db.session.commit()
    return camera
