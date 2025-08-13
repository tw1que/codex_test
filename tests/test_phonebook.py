import os
import sys
import tempfile
import io
import pytest
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from app.models import Contact, init_db, db


@pytest.fixture
def client():
    tmpdir = tempfile.TemporaryDirectory()
    db_path = os.path.join(tmpdir.name, 'test.db')
    app = create_app({
        'TESTING': True,
        'PHONEBOOK_PATH': os.path.join(tmpdir.name, 'pb.xml'),
        'SECRET_KEY': 'test',
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}'
    })
    with app.app_context():
        init_db()
    with app.test_client() as client:
        yield client
    tmpdir.cleanup()


def test_add_and_delete(client):
    response = client.post('/add', data={'name': 'John', 'telephone': '+31 6 28330622'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'John' in response.data

    response = client.post('/add', data={'name': 'Jane', 'telephone': '+31 6 11111111'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Jane' in response.data and b'John' in response.data

    with client.application.app_context():
        jane_id = Contact.query.filter_by(name='Jane').first().id
    response = client.post(f'/delete/{jane_id}', follow_redirects=True)
    assert b'Jane' not in response.data
    assert b'John' in response.data


def test_edit_contact(client):
    client.post('/add', data={'name': 'Jane', 'telephone': '+31 6 11111111'})
    with client.application.app_context():
        contact_id = Contact.query.filter_by(name='Jane').first().id
    response = client.post(
        f'/edit/{contact_id}',
        data={'name': 'Janet', 'telephone': '+31 6 22222222'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b'Janet' in response.data


def test_edit_out_of_range(client):
    client.post('/add', data={'name': 'Test', 'telephone': '+31 6 12345678'})
    response = client.get('/edit/999')
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
    response = client.post('/add', data={'name': '', 'telephone': 'abc'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Naam is verplicht.' in response.data
    assert b'Ongeldig telefoonnummer.' in response.data
    response = client.get('/')
    assert b'abc' not in response.data


def test_delete_out_of_range(client):
    client.post('/add', data={'name': 'Single', 'telephone': '+31 6 00000000'})
    response = client.post('/delete/999', follow_redirects=True)
    assert response.status_code == 200
    assert b'Single' in response.data


def test_import_with_invalid_rows(client):
    csv_data = "name,telephone\nValid,+31611111111\nBad,abc\nAnother,+31622222222"
    data = {
        'file': (io.BytesIO(csv_data.encode('utf-8')), 'contacts.csv'),
    }
    response = client.post('/import', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Valid' in response.data and b'Another' in response.data
    assert b'Bad' not in response.data


def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.data == b'OK'


def test_delete_via_delete_method(client):
    client.post('/add', data={'name': 'Temp', 'telephone': '+31 6 99999999'})
    with client.application.app_context():
        contact = Contact.query.filter_by(name='Temp').first()
        contact_id = contact.id
        count_before = Contact.query.count()
    response = client.delete(f'/delete/{contact_id}')
    assert response.status_code == 204
    with client.application.app_context():
        assert Contact.query.count() == count_before - 1


def _search_items(html, query):
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    for item in soup.select('.contact-item'):
        name = item.select_one('.contact-name').get_text().lower()
        phone = item.select_one('.contact-phone').get_text().lower()
        if query in name or query in phone:
            results.append(item)
    return results


def test_search_ignores_action_text(client):
    client.post('/add', data={'name': 'Anne', 'telephone': '+31611111111'})
    client.post('/add', data={'name': 'Eve', 'telephone': '+31622222222'})
    resp = client.get('/')
    matches = _search_items(resp.data.decode('utf-8'), 'b')
    assert len(matches) == 0

