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
    response = client.post('/add', data={'name': 'John', 'telephone': '+31 6 28330622', 'label': 'Kantoor'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'John' in response.data
    # delete contact
    response = client.post('/delete/0', follow_redirects=True)
    assert b'John' not in response.data


def test_edit_contact(client):
    client.post('/add', data={'name': 'Jane', 'telephone': '+31 6 11111111', 'label': ''})
    # edit contact
    response = client.post('/edit/0', data={'name': 'Janet', 'telephone': '+31 6 22222222', 'label': 'Priv'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Janet' in response.data


def test_import_contacts(client):
    csv_data = "name,telephone,label\nJohn,+31611111111,Kantoor\nJane,+31622222222,Priv"
    data = {
        'file': (csv_data.encode('utf-8'), 'contacts.csv'),
    }
    response = client.post('/import', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b'John' in response.data and b'Jane' in response.data
