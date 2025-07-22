import os
import tempfile
import pytest
from app import create_app
from app import models

@pytest.fixture
def client():
    tmpdir = tempfile.TemporaryDirectory()
    app = create_app({'TESTING': True, 'PHONEBOOK_PATH': os.path.join(tmpdir.name, 'pb.xml'), 'SECRET_KEY': 'test'})
    with app.test_client() as client:
        yield client
    tmpdir.cleanup()

def test_add_and_delete(client):
    # add contact
    response = client.post('/add', data={'name': 'John', 'telephone': '+12345', 'label': 'Kantoor'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'John' in response.data
    # delete contact
    response = client.post('/delete/0', follow_redirects=True)
    assert b'John' not in response.data


def test_edit_contact(client):
    client.post('/add', data={'name': 'Jane', 'telephone': '+67890', 'label': ''})
    # edit contact
    response = client.post('/edit/0', data={'name': 'Janet', 'telephone': '+67890', 'label': 'Priv'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Janet' in response.data
