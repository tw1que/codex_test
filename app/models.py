import xml.etree.ElementTree as ET
from pathlib import Path


def load_phonebook(path):
    path = Path(path)
    if not path.exists():
        root = ET.Element('YealinkIPPhoneDirectory')
        tree = ET.ElementTree(root)
        tree.write(path, encoding='utf-8', xml_declaration=True)
    tree = ET.parse(path)
    root = tree.getroot()
    contacts = []
    for entry in root.findall('DirectoryEntry'):
        name = entry.findtext('Name')
        tel_elem = entry.find('Telephone')
        if tel_elem is not None:
            tel = tel_elem.text
            label = tel_elem.get('label', '')
        else:
            tel = ''
            label = ''
        contacts.append({'name': name, 'telephone': tel, 'label': label})
    return contacts


def save_phonebook(path, contacts):
    root = ET.Element('YealinkIPPhoneDirectory')
    for c in contacts:
        entry = ET.SubElement(root, 'DirectoryEntry')
        ET.SubElement(entry, 'Name').text = c['name']
        tel = ET.SubElement(entry, 'Telephone')
        if c.get('label'):
            tel.set('label', c['label'])
        tel.text = c['telephone']
    tree = ET.ElementTree(root)
    tree.write(path, encoding='utf-8', xml_declaration=True)


def add_contact(path, name, telephone, label=''):
    contacts = load_phonebook(path)
    contacts.append({'name': name, 'telephone': telephone, 'label': label})
    save_phonebook(path, contacts)


def delete_contact(path, index):
    contacts = load_phonebook(path)
    if 0 <= index < len(contacts):
        contacts.pop(index)
        save_phonebook(path, contacts)
        return True
    return False


def update_contact(path, index, name, telephone, label=''):
    """Update an existing contact by index."""
    contacts = load_phonebook(path)
    if 0 <= index < len(contacts):
        contacts[index] = {
            'name': name,
            'telephone': telephone,
            'label': label,
        }
        save_phonebook(path, contacts)
        return True
    return False


def import_contacts(path, fileobj, validator):
    """Import contacts from a CSV ``fileobj``.

    ``validator`` is a callable like :func:`validate_contact` used to validate
    each row. Only valid contacts are appended. The function returns the number
    of successfully imported contacts.
    """
    import csv
    contacts = load_phonebook(path)
    reader = csv.DictReader(fileobj)
    added = 0
    for row in reader:
        name = row.get('name') or row.get('Name')
        telephone = row.get('telephone') or row.get('Telephone')
        label = row.get('label') or row.get('Label') or ''
        if validator(name, telephone):
            contacts.append({'name': name, 'telephone': telephone, 'label': label})
            added += 1
    if added:
        save_phonebook(path, contacts)
    return added
