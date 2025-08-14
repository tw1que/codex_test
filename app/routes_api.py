from flask import Blueprint, request, jsonify, current_app
import re

from .models import (
    Contact,
    Practice,
    Supplier,
    ContactPerson,
    PhoneNumber,
    PracticeContact,
    SupplierContact,
)
from .utils import validate_contact_data, PHONE_RE


api_bp = Blueprint('api', __name__, url_prefix='/api')
EMAIL_RE = re.compile(r'^[^@]+@[^@]+\.[^@]+$')


def _session():
    return current_app.config['SESSION_FACTORY']()


@api_bp.get('/contacts')
@api_bp.get('/contacts/')  # allow trailing slash

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


@api_bp.post('/contacts')
@api_bp.post('/contacts/')

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


@api_bp.put('/contacts/<int:contact_id>')

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


@api_bp.delete('/contacts/<int:contact_id>')

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


# ---------------------------------------------------------------------------
# Helper validators


def _valid_email(email: str | None) -> bool:
    return email is None or EMAIL_RE.match(email)


def _valid_phone(number: str | None) -> bool:
    return bool(number) and PHONE_RE.match(number)


# ---------------------------------------------------------------------------
# Practice CRUD


@api_bp.get('/practices')
def list_practices():
    session = _session()
    practices = session.query(Practice).order_by(Practice.name).all()
    result = [{'id': p.id, 'name': p.name, 'email': p.email} for p in practices]
    session.close()
    return jsonify(result)


@api_bp.post('/practices')
def create_practice():
    data = request.get_json(silent=True) or {}
    name = data.get('name')
    email = data.get('email')
    if not name or not _valid_email(email):
        return jsonify({'error': 'Invalid data'}), 400
    session = _session()
    practice = Practice(name=name, email=email)
    session.add(practice)
    session.commit()
    result = {'id': practice.id, 'name': practice.name, 'email': practice.email}
    session.close()
    return jsonify(result), 201


@api_bp.put('/practices/<int:practice_id>')
def update_practice(practice_id):
    data = request.get_json(silent=True) or {}
    session = _session()
    practice = session.get(Practice, practice_id)
    if not practice:
        session.close()
        return jsonify({'error': 'Not found'}), 404
    name = data.get('name', practice.name)
    email = data.get('email', practice.email)
    if not name or not _valid_email(email):
        session.close()
        return jsonify({'error': 'Invalid data'}), 400
    practice.name = name
    practice.email = email
    session.commit()
    result = {'id': practice.id, 'name': practice.name, 'email': practice.email}
    session.close()
    return jsonify(result)


@api_bp.delete('/practices/<int:practice_id>')
def delete_practice(practice_id):
    session = _session()
    practice = session.get(Practice, practice_id)
    if not practice:
        session.close()
        return jsonify({'error': 'Not found'}), 404
    session.delete(practice)
    session.commit()
    session.close()
    return ('', 204)


@api_bp.get('/practices/<int:practice_id>/phones')
def list_practice_phones(practice_id):
    session = _session()
    practice = session.get(Practice, practice_id)
    if not practice:
        session.close()
        return jsonify({'error': 'Not found'}), 404
    result = [{'id': pn.id, 'number': pn.number, 'type': pn.type} for pn in practice.phone_numbers]
    session.close()
    return jsonify(result)


@api_bp.post('/practices/<int:practice_id>/phones')
def add_practice_phone(practice_id):
    data = request.get_json(silent=True) or {}
    number = data.get('number')
    ptype = data.get('type')
    if not _valid_phone(number):
        return jsonify({'error': 'Invalid phone'}), 400
    session = _session()
    practice = session.get(Practice, practice_id)
    if not practice:
        session.close()
        return jsonify({'error': 'Not found'}), 404
    phone = PhoneNumber(number=number, type=ptype, practice=practice)
    session.add(phone)
    session.commit()
    result = {'id': phone.id, 'number': phone.number, 'type': phone.type}
    session.close()
    return jsonify(result), 201


@api_bp.get('/practices/<int:practice_id>/contacts')
def list_practice_contacts(practice_id):
    session = _session()
    practice = session.get(Practice, practice_id)
    if not practice:
        session.close()
        return jsonify({'error': 'Not found'}), 404
    result = [
        {
            'id': link.contact.id,
            'first_name': link.contact.first_name,
            'last_name': link.contact.last_name,
            'role': link.role,
            'is_primary': link.is_primary,
        }
        for link in practice.contacts
    ]
    session.close()
    return jsonify(result)


@api_bp.post('/practices/<int:practice_id>/contacts')
def link_practice_contact(practice_id):
    data = request.get_json(silent=True) or {}
    contact_id = data.get('contact_id')
    role = data.get('role')
    is_primary = bool(data.get('is_primary'))
    session = _session()
    practice = session.get(Practice, practice_id)
    contact = session.get(ContactPerson, contact_id)
    if not practice or not contact:
        session.close()
        return jsonify({'error': 'Not found'}), 404
    link = PracticeContact(practice=practice, contact=contact, role=role, is_primary=is_primary)
    session.add(link)
    session.commit()
    session.close()
    return ('', 204)


@api_bp.delete('/practices/<int:practice_id>/contacts/<int:contact_id>')
def unlink_practice_contact(practice_id, contact_id):
    session = _session()
    link = (
        session.query(PracticeContact)
        .filter_by(practice_id=practice_id, contact_id=contact_id)
        .first()
    )
    if not link:
        session.close()
        return jsonify({'error': 'Not found'}), 404
    session.delete(link)
    session.commit()
    session.close()
    return ('', 204)


# ---------------------------------------------------------------------------
# Supplier CRUD – mirrors practice endpoints


@api_bp.get('/suppliers')
def list_suppliers():
    session = _session()
    suppliers = session.query(Supplier).order_by(Supplier.name).all()
    result = [{'id': s.id, 'name': s.name, 'email': s.email} for s in suppliers]
    session.close()
    return jsonify(result)


@api_bp.post('/suppliers')
def create_supplier():
    data = request.get_json(silent=True) or {}
    name = data.get('name')
    email = data.get('email')
    if not name or not _valid_email(email):
        return jsonify({'error': 'Invalid data'}), 400
    session = _session()
    supplier = Supplier(name=name, email=email)
    session.add(supplier)
    session.commit()
    result = {'id': supplier.id, 'name': supplier.name, 'email': supplier.email}
    session.close()
    return jsonify(result), 201


@api_bp.put('/suppliers/<int:supplier_id>')
def update_supplier(supplier_id):
    data = request.get_json(silent=True) or {}
    session = _session()
    supplier = session.get(Supplier, supplier_id)
    if not supplier:
        session.close()
        return jsonify({'error': 'Not found'}), 404
    name = data.get('name', supplier.name)
    email = data.get('email', supplier.email)
    if not name or not _valid_email(email):
        session.close()
        return jsonify({'error': 'Invalid data'}), 400
    supplier.name = name
    supplier.email = email
    session.commit()
    result = {'id': supplier.id, 'name': supplier.name, 'email': supplier.email}
    session.close()
    return jsonify(result)


@api_bp.delete('/suppliers/<int:supplier_id>')
def delete_supplier(supplier_id):
    session = _session()
    supplier = session.get(Supplier, supplier_id)
    if not supplier:
        session.close()
        return jsonify({'error': 'Not found'}), 404
    session.delete(supplier)
    session.commit()
    session.close()
    return ('', 204)


@api_bp.get('/suppliers/<int:supplier_id>/phones')
def list_supplier_phones(supplier_id):
    session = _session()
    supplier = session.get(Supplier, supplier_id)
    if not supplier:
        session.close()
        return jsonify({'error': 'Not found'}), 404
    result = [{'id': pn.id, 'number': pn.number, 'type': pn.type} for pn in supplier.phone_numbers]
    session.close()
    return jsonify(result)


@api_bp.post('/suppliers/<int:supplier_id>/phones')
def add_supplier_phone(supplier_id):
    data = request.get_json(silent=True) or {}
    number = data.get('number')
    ptype = data.get('type')
    if not _valid_phone(number):
        return jsonify({'error': 'Invalid phone'}), 400
    session = _session()
    supplier = session.get(Supplier, supplier_id)
    if not supplier:
        session.close()
        return jsonify({'error': 'Not found'}), 404
    phone = PhoneNumber(number=number, type=ptype, supplier=supplier)
    session.add(phone)
    session.commit()
    result = {'id': phone.id, 'number': phone.number, 'type': phone.type}
    session.close()
    return jsonify(result), 201


@api_bp.get('/suppliers/<int:supplier_id>/contacts')
def list_supplier_contacts(supplier_id):
    session = _session()
    supplier = session.get(Supplier, supplier_id)
    if not supplier:
        session.close()
        return jsonify({'error': 'Not found'}), 404
    result = [
        {
            'id': link.contact.id,
            'first_name': link.contact.first_name,
            'last_name': link.contact.last_name,
            'role': link.role,
            'is_primary': link.is_primary,
        }
        for link in supplier.contacts
    ]
    session.close()
    return jsonify(result)


@api_bp.post('/suppliers/<int:supplier_id>/contacts')
def link_supplier_contact(supplier_id):
    data = request.get_json(silent=True) or {}
    contact_id = data.get('contact_id')
    role = data.get('role')
    is_primary = bool(data.get('is_primary'))
    session = _session()
    supplier = session.get(Supplier, supplier_id)
    contact = session.get(ContactPerson, contact_id)
    if not supplier or not contact:
        session.close()
        return jsonify({'error': 'Not found'}), 404
    link = SupplierContact(supplier=supplier, contact=contact, role=role, is_primary=is_primary)
    session.add(link)
    session.commit()
    session.close()
    return ('', 204)


@api_bp.delete('/suppliers/<int:supplier_id>/contacts/<int:contact_id>')
def unlink_supplier_contact(supplier_id, contact_id):
    session = _session()
    link = (
        session.query(SupplierContact)
        .filter_by(supplier_id=supplier_id, contact_id=contact_id)
        .first()
    )
    if not link:
        session.close()
        return jsonify({'error': 'Not found'}), 404
    session.delete(link)
    session.commit()
    session.close()
    return ('', 204)


# ---------------------------------------------------------------------------
# Contact person CRUD


@api_bp.get('/contact-persons')
def list_contact_persons():
    session = _session()
    persons = session.query(ContactPerson).order_by(ContactPerson.last_name).all()
    result = [
        {
            'id': p.id,
            'first_name': p.first_name,
            'last_name': p.last_name,
            'email': p.email,
            'function': p.function,
        }
        for p in persons
    ]
    session.close()
    return jsonify(result)


@api_bp.post('/contact-persons')
def create_contact_person():
    data = request.get_json(silent=True) or {}
    first = data.get('first_name')
    last = data.get('last_name')
    email = data.get('email')
    function = data.get('function')
    if not first or not last or not _valid_email(email):
        return jsonify({'error': 'Invalid data'}), 400
    session = _session()
    person = ContactPerson(first_name=first, last_name=last, email=email, function=function)
    session.add(person)
    session.commit()
    result = {
        'id': person.id,
        'first_name': person.first_name,
        'last_name': person.last_name,
        'email': person.email,
        'function': person.function,
    }
    session.close()
    return jsonify(result), 201


@api_bp.put('/contact-persons/<int:person_id>')
def update_contact_person(person_id):
    data = request.get_json(silent=True) or {}
    session = _session()
    person = session.get(ContactPerson, person_id)
    if not person:
        session.close()
        return jsonify({'error': 'Not found'}), 404
    first = data.get('first_name', person.first_name)
    last = data.get('last_name', person.last_name)
    email = data.get('email', person.email)
    function = data.get('function', person.function)
    if not first or not last or not _valid_email(email):
        session.close()
        return jsonify({'error': 'Invalid data'}), 400
    person.first_name = first
    person.last_name = last
    person.email = email
    person.function = function
    session.commit()
    result = {
        'id': person.id,
        'first_name': person.first_name,
        'last_name': person.last_name,
        'email': person.email,
        'function': person.function,
    }
    session.close()
    return jsonify(result)


@api_bp.delete('/contact-persons/<int:person_id>')
def delete_contact_person(person_id):
    session = _session()
    person = session.get(ContactPerson, person_id)
    if not person:
        session.close()
        return jsonify({'error': 'Not found'}), 404
    session.delete(person)
    session.commit()
    session.close()
    return ('', 204)


@api_bp.get('/contact-persons/<int:person_id>/phones')
def list_contact_person_phones(person_id):
    session = _session()
    person = session.get(ContactPerson, person_id)
    if not person:
        session.close()
        return jsonify({'error': 'Not found'}), 404
    result = [{'id': pn.id, 'number': pn.number, 'type': pn.type} for pn in person.phone_numbers]
    session.close()
    return jsonify(result)


@api_bp.post('/contact-persons/<int:person_id>/phones')
def add_contact_person_phone(person_id):
    data = request.get_json(silent=True) or {}
    number = data.get('number')
    ptype = data.get('type')
    if not _valid_phone(number):
        return jsonify({'error': 'Invalid phone'}), 400
    session = _session()
    person = session.get(ContactPerson, person_id)
    if not person:
        session.close()
        return jsonify({'error': 'Not found'}), 404
    phone = PhoneNumber(number=number, type=ptype, contact_person=person)
    session.add(phone)
    session.commit()
    result = {'id': phone.id, 'number': phone.number, 'type': phone.type}
    session.close()
    return jsonify(result), 201
