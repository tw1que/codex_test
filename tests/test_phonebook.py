import os
import tempfile
import io
import pytest
from app import create_app
from app.models import load_phonebook

@pytest.fixture
def client():
    tmpdir = tempfile.TemporaryDirectory()
    app = create_app({'TESTING': True, 'PHONEBOOK_PATH': os.path.join(tmpdir.name, 'pb.xml'), 'SECRET_KEY': 'test'})
    with app.test_client() as client:
        yield client
    tmpdir.cleanup()

def test_add_and_delete(client):
    # add first contact
    response = client.post('/add', data={'name': 'John', 'telephone': '+31 6 28330622'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'John' in response.data

    # add second contact
    response = client.post('/add', data={'name': 'Jane', 'telephone': '+31 6 11111111'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Jane' in response.data and b'John' in response.data

    # delete contact "Jane" by finding its sorted index
    path = client.application.config['PHONEBOOK_PATH']
    contacts = load_phonebook(path)
    jane_index = next(i for i, c in enumerate(contacts) if c['name'] == 'Jane')
    response = client.post(f'/delete/{jane_index}', follow_redirects=True)
    assert b'Jane' not in response.data
    assert b'John' in response.data


def test_edit_contact(client):
    client.post('/add', data={'name': 'Jane', 'telephone': '+31 6 11111111'})
    # edit contact
    response = client.post('/edit/0', data={'name': 'Janet', 'telephone': '+31 6 22222222'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Janet' in response.data

def test_edit_out_of_range(client):
    client.post('/add', data={'name': 'Test', 'telephone': '+31 6 12345678'})
    # attempt to edit non-existent contact should 404
    response = client.get('/edit/5')
    assert response.status_code == 404


def test_import_contacts(client):
    csv_data = "name,telephone\nJohn,+31611111111\nJane,+31622222222"
    data = {
        'file': (io.BytesIO(csv_data.encode('utf-8')), 'contacts.csv'),
    }
    response = client.post('/import', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'John' in response.data and b'Jane' in response.data

def test_invalid_add_contact(client):
    # missing name and invalid phone number
    response = client.post('/add', data={'name': '', 'telephone': 'abc'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Naam is verplicht.' in response.data
    assert b'Ongeldig telefoonnummer.' in response.data
    # no contacts should have been added
    response = client.get('/')
    assert b'abc' not in response.data

def test_delete_out_of_range(client):
    # add one valid contact
    client.post('/add', data={'name': 'Single', 'telephone': '+31 6 00000000'})
    # attempt to delete non-existent index
    response = client.post('/delete/5', follow_redirects=True)
    assert response.status_code == 200
    # contact should still exist
    assert b'Single' in response.data

def test_import_with_invalid_rows(client):
    csv_data = "name,telephone\nValid,+31611111111\nBad,abc\nAnother,+31622222222"
    data = {
        'file': (io.BytesIO(csv_data.encode('utf-8')), 'contacts.csv'),
    }
    response = client.post('/import', data=data, follow_redirects=True)
    assert response.status_code == 200
    # only valid rows should be imported
    assert b'Valid' in response.data and b'Another' in response.data
    assert b'Bad' not in response.data


def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.data == b'OK'


def test_delete_via_delete_method(client):
    client.post('/add', data={'name': 'Temp', 'telephone': '+31 6 99999999'})
    path = client.application.config['PHONEBOOK_PATH']
    contacts = load_phonebook(path)
    index = next(i for i, c in enumerate(contacts) if c['name'] == 'Temp')
    response = client.delete(f'/delete/{index}')
    assert response.status_code == 204
    contacts_after = load_phonebook(path)
    assert len(contacts_after) == len(contacts) - 1
