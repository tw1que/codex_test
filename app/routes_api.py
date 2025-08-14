from flask import Blueprint, request, jsonify, current_app

from .models import Contact
from .utils import validate_contact_data


api_bp = Blueprint('api', __name__, url_prefix='/api/contacts')


def _session():
    return current_app.config['SESSION_FACTORY']()


@api_bp.get('')
@api_bp.get('/')  # allow trailing slash

def list_contacts():
    session = _session()
    query = session.query(Contact).filter(Contact.active == True)  # noqa: E712
    q = request.args.get('q', '').strip().lower()
    if q:
        query = query.filter(
            (Contact.name.ilike(f'%{q}%')) | (Contact.telephone.ilike(f'%{q}%'))
        )
    category = request.args.get('category', '').strip()
    if category:
        query = query.filter(Contact.category == category)
    contacts = query.order_by(Contact.name).all()
    result = [
        {
            'id': c.id,
            'name': c.name,
            'telephone': c.telephone,
            'category': c.category,
        }
        for c in contacts
    ]
    session.close()
    return jsonify(result)


@api_bp.post('')
@api_bp.post('/')

def create_contact():
    data = request.get_json(silent=True) or {}
    name = data.get('name')
    telephone = data.get('telephone')
    category = data.get('category', 'other')
    valid, messages = validate_contact_data(name, telephone)
    if not valid:
        return jsonify({'error': messages[0]}), 400
    session = _session()
    contact = Contact(name=name, telephone=telephone, category=category)
    session.add(contact)
    session.commit()
    result = {
        'id': contact.id,
        'name': contact.name,
        'telephone': contact.telephone,
        'category': contact.category,
    }
    session.close()
    return jsonify(result), 201


@api_bp.put('/<int:contact_id>')

def update_contact(contact_id):
    data = request.get_json(silent=True) or {}
    session = _session()
    contact = session.get(Contact, contact_id)
    if not contact or not contact.active:
        session.close()
        return jsonify({'error': 'Not found'}), 404
    name = data.get('name', contact.name)
    telephone = data.get('telephone', contact.telephone)
    category = data.get('category', contact.category)
    valid, messages = validate_contact_data(name, telephone)
    if not valid:
        session.close()
        return jsonify({'error': messages[0]}), 400
    contact.name = name
    contact.telephone = telephone
    contact.category = category
    session.commit()
    result = {
        'id': contact.id,
        'name': contact.name,
        'telephone': contact.telephone,
        'category': contact.category,
    }
    session.close()
    return jsonify(result)


@api_bp.delete('/<int:contact_id>')

def delete_contact(contact_id):
    session = _session()
    contact = session.get(Contact, contact_id)
    if not contact or not contact.active:
        session.close()
        return jsonify({'error': 'Not found'}), 404
    contact.active = False
    session.commit()
    session.close()
    return ('', 204)
