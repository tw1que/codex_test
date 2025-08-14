import re
from flask import flash

# Accept phone numbers with optional spaces, e.g. "+31 6 28330622"
# First check allowed characters (digits, spaces and an optional leading plus)
PHONE_RE = re.compile(r'^\+?[0-9 ]+$')


def validate_contact_data(name: str | None, telephone: str | None):
    """Validate a contact and return ``(valid, messages)``.

    ``messages`` is a list of error strings.  This helper performs the actual
    validation without flashing so it can be reused by the JSON API.
    """

    messages: list[str] = []
    if not name:
        messages.append('Naam is verplicht.')
    if not telephone or not PHONE_RE.match(telephone):
        messages.append('Ongeldig telefoonnummer.')
    else:
        digits = telephone.replace(' ', '').lstrip('+')
        if not digits.isdigit() or len(digits) > 15:
            messages.append('Ongeldig telefoonnummer.')
    return (len(messages) == 0, messages)


def validate_contact(name: str | None, telephone: str | None) -> bool:
    """UI validator that flashes messages on failure.

    Returns ``True`` when the contact details are valid.
    """

    valid, messages = validate_contact_data(name, telephone)
    if not valid:
        for msg in messages:
            flash(msg, 'error')
    return valid
