import re
from flask import flash

PHONE_RE = re.compile(r'^\+?\d{1,15}$')


def validate_contact(name, telephone):
    valid = True
    if not name:
        flash('Naam is verplicht.', 'error')
        valid = False
    if not telephone or not PHONE_RE.match(telephone):
        flash('Ongeldig telefoonnummer.', 'error')
        valid = False
    return valid
