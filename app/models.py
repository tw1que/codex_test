from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from pathlib import Path
import xml.etree.ElementTree as ET


db = SQLAlchemy()


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)


def init_db():
    """Create all tables and import contacts from phonebook.xml if empty."""
    db.create_all()
    if Contact.query.first() is not None:
        return
    path = Path(current_app.config["PHONEBOOK_PATH"])
    if not path.exists():
        return
    tree = ET.parse(path)
    root = tree.getroot()
    for entry in root.findall('DirectoryEntry'):
        name = entry.findtext('Name')
        telephone = entry.findtext('Telephone') or ''
        if name:
            db.session.add(Contact(name=name, telephone=telephone))
    db.session.commit()
