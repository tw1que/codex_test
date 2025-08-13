from flask import Blueprint, render_template, request, redirect, url_for, abort, flash, jsonify
from io import TextIOWrapper
from .models import Contact, db
from .utils import validate_contact

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    contacts = Contact.query.order_by(Contact.name).all()
    return render_template('index.html', contacts=contacts)


@main_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form.get('name')
        telephone = request.form.get('telephone')
        if validate_contact(name, telephone):
            db.session.add(Contact(name=name, telephone=telephone))
            db.session.commit()
            return redirect(url_for('main.index'))
    return render_template('add.html')


@main_bp.route('/delete/<int:contact_id>', methods=['POST', 'DELETE'])
def delete(contact_id):
    contact = Contact.query.get(contact_id)
    success = False
    if contact:
        db.session.delete(contact)
        db.session.commit()
        success = True
    if request.method == 'POST':
        return redirect(url_for('main.index'))
    if success:
        return ('', 204)
    return jsonify({'error': 'Not found'}), 404


@main_bp.route('/edit/<int:contact_id>', methods=['GET', 'POST'])
def edit(contact_id):
    contact = Contact.query.get(contact_id)
    if contact is None:
        abort(404)
    if request.method == 'POST':
        name = request.form.get('name')
        telephone = request.form.get('telephone')
        if validate_contact(name, telephone):
            contact.name = name
            contact.telephone = telephone
            db.session.commit()
            return redirect(url_for('main.index'))
    return render_template('edit.html', contact=contact)


@main_bp.route('/import', methods=['GET', 'POST'])
def import_view():
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            text_file = TextIOWrapper(file.stream, encoding='utf-8')
            import csv
            reader = csv.DictReader(text_file)
            added = 0
            for row in reader:
                name = row.get('name') or row.get('Name')
                telephone = row.get('telephone') or row.get('Telephone')
                if validate_contact(name, telephone):
                    db.session.add(Contact(name=name, telephone=telephone))
                    added += 1
            if added:
                db.session.commit()
                flash(f"{added} contacten ge\u00efmporteerd.", "info")
            return redirect(url_for('main.index'))
        flash('Geen bestand ge\u00fcppload.', 'error')
    return render_template('import.html')
