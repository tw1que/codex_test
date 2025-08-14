from flask import current_app
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
import csv
import xml.etree.ElementTree as ET

Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    telephone = Column(String, nullable=False)
    category = Column(String, nullable=False, default='other')
    active = Column(Boolean, nullable=False, default=True)


# ---------------------------------------------------------------------------
# New models for a flexible contact database used by the dental lab.  These
# models are intentionally kept simple but illustrate how the schema can grow
# beyond the original single ``Contact`` table.  The ``Order`` entity mentioned
# in the requirements can later reference ``Practice``, ``Supplier`` and
# ``ContactPerson`` using foreign keys similar to those used below.


class Address(Base):
    """Generic postal address that can be linked to practices or suppliers."""

    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    street = Column(String)
    number = Column(String)
    postal_code = Column(String)
    city = Column(String)
    country = Column(String)


class Practice(Base):
    """Dental practice that sends work to the lab."""

    __tablename__ = 'practices'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String)
    address_id = Column(Integer, ForeignKey('addresses.id'))

    address = relationship('Address')
    phone_numbers = relationship('PhoneNumber', back_populates='practice')
    contacts = relationship('PracticeContact', back_populates='practice', cascade='all, delete-orphan')
    contact_persons = relationship('ContactPerson', secondary='practice_contacts', viewonly=True, back_populates='practices')


class Supplier(Base):
    """External supplier of materials or services."""

    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String)
    address_id = Column(Integer, ForeignKey('addresses.id'))

    address = relationship('Address')
    phone_numbers = relationship('PhoneNumber', back_populates='supplier')
    contacts = relationship('SupplierContact', back_populates='supplier', cascade='all, delete-orphan')
    contact_persons = relationship('ContactPerson', secondary='supplier_contacts', viewonly=True, back_populates='suppliers')


class ContactPerson(Base):
    """A person working for a practice or supplier."""

    __tablename__ = 'contact_persons'
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String)
    function = Column(String)

    phone_numbers = relationship('PhoneNumber', back_populates='contact_person')
    practice_links = relationship('PracticeContact', back_populates='contact', cascade='all, delete-orphan')
    supplier_links = relationship('SupplierContact', back_populates='contact', cascade='all, delete-orphan')
    practices = relationship('Practice', secondary='practice_contacts', viewonly=True, back_populates='contact_persons')
    suppliers = relationship('Supplier', secondary='supplier_contacts', viewonly=True, back_populates='contact_persons')


class PhoneNumber(Base):
    """Phone number belonging to a practice, supplier or contact person."""

    __tablename__ = 'phone_numbers'
    id = Column(Integer, primary_key=True)
    number = Column(String, nullable=False)
    type = Column(String)
    practice_id = Column(Integer, ForeignKey('practices.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    contact_person_id = Column(Integer, ForeignKey('contact_persons.id'))

    practice = relationship('Practice', back_populates='phone_numbers')
    supplier = relationship('Supplier', back_populates='phone_numbers')
    contact_person = relationship('ContactPerson', back_populates='phone_numbers')


class PracticeContact(Base):
    """Association table linking practices and contact persons."""

    __tablename__ = 'practice_contacts'
    practice_id = Column(Integer, ForeignKey('practices.id'), primary_key=True)
    contact_id = Column(Integer, ForeignKey('contact_persons.id'), primary_key=True)
    role = Column(String)
    is_primary = Column(Boolean, nullable=False, default=False)

    practice = relationship('Practice', back_populates='contacts')
    contact = relationship('ContactPerson', back_populates='practice_links')


class SupplierContact(Base):
    """Association table linking suppliers and contact persons."""

    __tablename__ = 'supplier_contacts'
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), primary_key=True)
    contact_id = Column(Integer, ForeignKey('contact_persons.id'), primary_key=True)
    role = Column(String)
    is_primary = Column(Boolean, nullable=False, default=False)

    supplier = relationship('Supplier', back_populates='contacts')
    contact = relationship('ContactPerson', back_populates='supplier_links')


def _get_session():
    """Return a new SQLAlchemy session using the app's session factory."""
    Session = current_app.config['SESSION_FACTORY']
    return Session()


def load_phonebook():
    """Return all active contacts ordered by name as a list of dicts."""
    session = _get_session()
    contacts = (
        session.query(Contact)
        .filter(Contact.active == True)  # noqa: E712
        .order_by(Contact.name)
        .all()
    )
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
    return result


def add_contact(name, telephone, category='other'):
    session = _get_session()
    session.add(Contact(name=name, telephone=telephone, category=category))
    session.commit()
    session.close()


def delete_contact(index):
    session = _get_session()
    contacts = (
        session.query(Contact)
        .filter(Contact.active == True)  # noqa: E712
        .order_by(Contact.name)
        .all()
    )
    if 0 <= index < len(contacts):
        contacts[index].active = False
        session.commit()
        session.close()
        return True
    session.close()
    return False


def update_contact(index, name, telephone, category='other'):
    session = _get_session()
    contacts = (
        session.query(Contact)
        .filter(Contact.active == True)  # noqa: E712
        .order_by(Contact.name)
        .all()
    )
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


def import_contacts_xml(fileobj, validator, category="other"):
    """Import contacts from Yealink XML files.

    Supports the current ``YealinkIPPhoneDirectory`` export format as well as
    the legacy ``YealinkIPPhoneBook`` structure previously used in this
    project.  Other XML structures are ignored.
    """

    session = _get_session()
    tree = ET.parse(fileobj)
    root = tree.getroot()

    added = 0

    # Modern format: <YealinkIPPhoneDirectory><DirectoryEntry>...</DirectoryEntry></YealinkIPPhoneDirectory>
    entries = root.findall("DirectoryEntry")
    if entries:
        for entry in entries:
            name = entry.findtext("Name")
            telephone = entry.findtext("Telephone")
            if validator(name, telephone):
                session.add(Contact(name=name, telephone=telephone, category=category))
                added += 1
    else:
        # Legacy format: <YealinkIPPhoneBook><Directory><Unit Name=".." Phone1=".."/></Directory></YealinkIPPhoneBook>
        for unit in root.findall("./Directory/Unit"):
            name = unit.attrib.get("Name")
            telephone = unit.attrib.get("Phone1")
            if validator(name, telephone):
                session.add(Contact(name=name, telephone=telephone, category=category))
                added += 1

    if added:
        session.commit()
    else:
        session.rollback()
    session.close()
    return added
