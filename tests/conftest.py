import flask_migrate
import pytest
from datetime import datetime
from app import create_app
from app.dbmodels.user import User
from app import db

@pytest.fixture
def client():
    app = create_app("testing")
    with app.app_context():
        with app.test_client() as client:
            flask_migrate.upgrade()
            new_user = User(
                email="test@user.com",
                username="test.User",
                name="Test User",
                password="test1234",
                joined_date=datetime.utcnow(),
            )
            db.session.add(new_user)
            db.session.flush()   
            # Commit changes to DB
            db.session.commit()

            yield client

        