import os
import sys
import tempfile
import io
import pytest
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

# Ensure the application package is importable when tests are run directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import load_phonebook

@pytest.fixture
def client():
    tmpdir = tempfile.TemporaryDirectory()
    db_path = os.path.join(tmpdir.name, 'pb.sqlite')
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}', 'SECRET_KEY': 'test'})
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
    contacts = load_phonebook()
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


def test_flash_message_styling(client):
    # trigger error flash
    resp = client.post('/import', data={}, follow_redirects=True)
    soup = BeautifulSoup(resp.data, 'html.parser')
    li = soup.select_one('ul li')
    assert 'text-red-600' in li.get('class', [])

    # trigger info flash
    csv_data = "name,telephone\nJohn,+31611111111"
    data = {
        'file': (io.BytesIO(csv_data.encode('utf-8')), 'contacts.csv'),
    }
    resp = client.post('/import', data=data, follow_redirects=True)
    soup = BeautifulSoup(resp.data, 'html.parser')
    li = soup.select_one('ul li')
    assert 'text-green-600' in li.get('class', [])

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
    contacts = load_phonebook()
    index = next(i for i, c in enumerate(contacts) if c['name'] == 'Temp')
    response = client.delete(f'/delete/{index}')
    assert response.status_code == 204
    contacts_after = load_phonebook()
    assert len(contacts_after) == len(contacts) - 1


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


def test_all_xml_with_etag(client):
    """Ensure the XML export and caching headers work."""
    client.post('/add', data={'name': 'Bob', 'telephone': '+31612345678'})
    response = client.get('/phonebook/all.xml')
    assert response.status_code == 200
    assert response.headers['Content-Type'].startswith('application/xml')
    etag = response.headers['ETag']
    last_modified = response.headers['Last-Modified']
    root = ET.fromstring(response.data)
    entries = root.findall('DirectoryEntry')
    assert any(e.findtext('Name') == 'Bob' and e.findtext('Telephone') == '+31612345678' for e in entries)
    response2 = client.get('/phonebook/all.xml', headers={'If-None-Match': etag, 'If-Modified-Since': last_modified})
    assert response2.status_code == 304


def test_root_xml_menu(client):
    response = client.get('/phonebook/root.xml')
    assert response.status_code == 200
    root = ET.fromstring(response.data)
    names = [mi.findtext('Name') for mi in root.findall('MenuItem')]
    assert 'All' in names and 'Practices' in names and 'Suppliers' in names


def test_auto_import(tmp_path):
    """Database should auto-import contacts from an initial XML file."""
    xml_content = (
        "<?xml version='1.0' encoding='UTF-8'?>"\
        "<YealinkIPPhoneDirectory>"\
        "<DirectoryEntry><Name>Alice</Name><Telephone>+31611111111"\
        "</Telephone></DirectoryEntry>"\
        "</YealinkIPPhoneDirectory>"
    )
    xml_file = tmp_path / "phonebook.xml"
    xml_file.write_text(xml_content, encoding="utf-8")
    db_path = tmp_path / "pb.sqlite"
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'INITIAL_PHONEBOOK_XML': str(xml_file),
        'SECRET_KEY': 'test'
    })
    with app.app_context():
        contacts = load_phonebook()
    assert len(contacts) == 1
    assert contacts[0]['name'] == 'Alice'
