import os
import os
import sys
import tempfile
import xml.etree.ElementTree as ET
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app


@pytest.fixture
def client():
    tmpdir = tempfile.TemporaryDirectory()
    db_path = os.path.join(tmpdir.name, 'pb.sqlite')
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}', 'SECRET_KEY': 'test'})
    with app.test_client() as client:
        yield client
    tmpdir.cleanup()


def test_csv_export(client):
    client.post('/add', data={'name': 'Alice', 'telephone': '+311', 'category': 'practice'})
    client.post('/add', data={'name': 'Bob', 'telephone': '+322', 'category': 'supplier'})
    resp = client.get('/export/contacts.csv')
    assert resp.status_code == 200
    text = resp.data.decode('utf-8').strip().splitlines()
    assert text[0] == 'name,telephone,category'
    assert len(text) == 3


def test_vcf_export(client):
    client.post('/add', data={'name': 'Alice Example', 'telephone': '+311'})
    resp = client.get('/export/contacts.vcf')
    assert resp.status_code == 200
    data = resp.data.decode('utf-8')
    assert 'FN:Alice Example' in data
    assert 'TEL;TYPE=CELL:+311' in data


def test_category_xml(client):
    client.post('/add', data={'name': 'P1', 'telephone': '+111', 'category': 'practice'})
    client.post('/add', data={'name': 'S1', 'telephone': '+222', 'category': 'supplier'})
    resp = client.get('/phonebook/practices.xml')
    root = ET.fromstring(resp.data)
    names = [e.findtext('Name') for e in root.findall('DirectoryEntry')]
    assert 'P1' in names and 'S1' not in names
    resp = client.get('/phonebook/suppliers.xml')
    root = ET.fromstring(resp.data)
    names = [e.findtext('Name') for e in root.findall('DirectoryEntry')]
    assert 'S1' in names and 'P1' not in names
