from flask import Blueprint, Response, current_app

from .models import Contact


export_bp = Blueprint('export', __name__, url_prefix='/export')


def _session():
    return current_app.config['SESSION_FACTORY']()


@export_bp.route('/contacts.csv')
def export_csv():
    session = _session()
    contacts = session.query(Contact).order_by(Contact.name).all()
    session.close()

    def generate():
        yield 'name,telephone,category\n'
        for c in contacts:
            yield f'{c.name},{c.telephone},{c.category}\n'

    headers = {
        'Content-Disposition': 'attachment; filename=contacts.csv'
    }
    return Response(generate(), mimetype='text/csv', headers=headers)


@export_bp.route('/contacts.vcf')
def export_vcf():
    session = _session()
    contacts = session.query(Contact).order_by(Contact.name).all()
    session.close()

    def generate():
        for c in contacts:
            parts = c.name.split(' ', 1)
            first = parts[0]
            last = parts[1] if len(parts) > 1 else ''
            full = c.name
            yield 'BEGIN:VCARD\n'
            yield 'VERSION:3.0\n'
            yield f'N:{last};{first}\n'
            yield f'FN:{full}\n'
            yield f'TEL;TYPE=CELL:{c.telephone}\n'
            yield 'END:VCARD\n'

    headers = {
        'Content-Disposition': 'attachment; filename=contacts.vcf'
    }
    return Response(generate(), mimetype='text/vcard', headers=headers)
