import re
from flask import flash

# Accept phone numbers with optional spaces, e.g. "+31 6 28330622"
# First check allowed characters (digits, spaces and an optional leading plus)
PHONE_RE = re.compile(r'^\+?[0-9 ]+$')


def validate_contact(name, telephone):
    valid = True
    if not name:
        flash('Naam is verplicht.', 'error')
        valid = False
    if not telephone or not PHONE_RE.match(telephone):
        flash('Ongeldig telefoonnummer.', 'error')
        valid = False
    else:
        digits = telephone.replace(' ', '').lstrip('+')
        if not digits.isdigit() or len(digits) > 15:
            flash('Ongeldig telefoonnummer.', 'error')
            valid = False
    return valid
