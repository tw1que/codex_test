from __future__ import annotations

from hashlib import md5
from datetime import datetime, timezone
from email.utils import format_datetime, parsedate_to_datetime
from flask import Blueprint, Response, current_app, request, url_for
import xml.etree.ElementTree as ET
import os

from .models import Contact

xml_bp = Blueprint('xml', __name__, url_prefix='/phonebook')


def _db_timestamp() -> datetime:
    db_path = current_app.config['DB_PATH']
    return datetime.fromtimestamp(os.path.getmtime(db_path), tz=timezone.utc)


def _xml_response(xml_bytes: bytes) -> Response:
    etag = md5(xml_bytes).hexdigest()
    last_modified = _db_timestamp()
    headers = {
        'ETag': etag,
        'Last-Modified': format_datetime(last_modified, usegmt=True),
        'Content-Type': 'application/xml',
    }
    if request.headers.get('If-None-Match') == etag:
        return Response(status=304, headers=headers)
    ims = request.headers.get('If-Modified-Since')
    if ims:
        try:
            ims_dt = parsedate_to_datetime(ims)
            if ims_dt >= last_modified.replace(microsecond=0):
                return Response(status=304, headers=headers)
        except Exception:
            pass
    return Response(xml_bytes, headers=headers)


@xml_bp.route('/root.xml')
def root_xml() -> Response:
    root = ET.Element('YealinkIPPhoneDirectory')
    items = [
        ('All', url_for('xml.all_xml', _external=False)),
        ('Practices', url_for('xml.practices_xml', _external=False)),
        ('Suppliers', url_for('xml.suppliers_xml', _external=False)),
    ]
    for name, url in items:
        mi = ET.SubElement(root, 'MenuItem')
        ET.SubElement(mi, 'Name').text = name
        ET.SubElement(mi, 'URL').text = url
    xml_bytes = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    return _xml_response(xml_bytes)


def _contacts_xml(category: str | None = None) -> bytes:
    session = current_app.config['SESSION_FACTORY']()
    query = session.query(Contact)
    if category:
        query = query.filter(Contact.category == category)
    contacts = query.order_by(Contact.name).all()
    session.close()
    root = ET.Element('YealinkIPPhoneDirectory')
    for c in contacts:
        entry = ET.SubElement(root, 'DirectoryEntry')
        ET.SubElement(entry, 'Name').text = c.name
        ET.SubElement(entry, 'Telephone').text = c.telephone
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


@xml_bp.route('/all.xml')
def all_xml() -> Response:
    return _xml_response(_contacts_xml())


@xml_bp.route('/practices.xml')
def practices_xml() -> Response:
    return _xml_response(_contacts_xml('practice'))


@xml_bp.route('/suppliers.xml')
def suppliers_xml() -> Response:
    return _xml_response(_contacts_xml('supplier'))
