import re

import pytest

from app import create_app
from app.extensions import db


@pytest.fixture()
def app():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://", "SECRET_KEY": "test"})
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def csrf(client, path="/login"):
    html = client.get(path).get_data(as_text=True)
    return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)


@pytest.fixture()
def logged_in(client):
    token = csrf(client, "/register")
    client.post("/register", data={"email": "a@example.com", "password": "password123", "csrf_token": token})
    return client
