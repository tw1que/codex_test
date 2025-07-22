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
