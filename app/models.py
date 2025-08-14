from flask import current_app
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
import csv
import xml.etree.ElementTree as ET

Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    telephone = Column(String, nullable=False)
    category = Column(String, nullable=False, default='other')


def _get_session():
    """Return a new SQLAlchemy session using the app's session factory."""
    Session = current_app.config['SESSION_FACTORY']
    return Session()


def load_phonebook():
    """Return all contacts ordered by name as a list of dicts."""
    session = _get_session()
    contacts = session.query(Contact).order_by(Contact.name).all()
    result = [{'name': c.name, 'telephone': c.telephone} for c in contacts]
    session.close()
    return result


def add_contact(name, telephone, category='other'):
    session = _get_session()
    session.add(Contact(name=name, telephone=telephone, category=category))
    session.commit()
    session.close()


def delete_contact(index):
    session = _get_session()
    contacts = session.query(Contact).order_by(Contact.name).all()
    if 0 <= index < len(contacts):
        session.delete(contacts[index])
        session.commit()
        session.close()
        return True
    session.close()
    return False


def update_contact(index, name, telephone, category='other'):
    session = _get_session()
    contacts = session.query(Contact).order_by(Contact.name).all()
    if 0 <= index < len(contacts):
        contact = contacts[index]
        contact.name = name
        contact.telephone = telephone
        contact.category = category
        session.commit()
        session.close()
        return True
    session.close()
    return False


def import_contacts(fileobj, validator, category='other'):
    session = _get_session()
    reader = csv.DictReader(fileobj)
    added = 0
    for row in reader:
        name = row.get('name') or row.get('Name')
        telephone = row.get('telephone') or row.get('Telephone')
        if validator(name, telephone):
            session.add(Contact(name=name, telephone=telephone, category=category))
            added += 1
    if added:
        session.commit()
    else:
        session.rollback()
    session.close()
    return added


def import_contacts_xml(fileobj, validator, category='other'):
    session = _get_session()
    tree = ET.parse(fileobj)
    root = tree.getroot()
    added = 0
    for entry in root.findall('DirectoryEntry'):
        name = entry.findtext('Name')
        telephone = entry.findtext('Telephone')
        if validator(name, telephone):
            session.add(Contact(name=name, telephone=telephone, category=category))
            added += 1
    if added:
        session.commit()
    else:
        session.rollback()
    session.close()
    return added
