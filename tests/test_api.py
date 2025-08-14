import os
import sys
import tempfile
import pytest

# Ensure application importable
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


def test_api_crud(client):
    # Create
    resp = client.post('/api/contacts', json={'name': 'Bob', 'telephone': '+31612345678', 'category': 'practice'})
    assert resp.status_code == 201
    data = resp.get_json()
    cid = data['id']
    assert data['category'] == 'practice'

    # List
    resp = client.get('/api/contacts')
    assert resp.status_code == 200
    data = resp.get_json()
    assert any(c['id'] == cid for c in data)

    # Update
    resp = client.put(f'/api/contacts/{cid}', json={'telephone': '+31699999999', 'category': 'supplier'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['telephone'] == '+31699999999'
    assert data['category'] == 'supplier'

    # Delete
    resp = client.delete(f'/api/contacts/{cid}')
    assert resp.status_code == 204
    # Ensure gone
    resp = client.get('/api/contacts')
    data = resp.get_json()
    assert all(c['id'] != cid for c in data)

    # 404 paths
    assert client.put('/api/contacts/999', json={'name': 'x'}).status_code == 404
    assert client.delete('/api/contacts/999').status_code == 404
