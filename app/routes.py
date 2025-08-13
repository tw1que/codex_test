from flask import Blueprint, render_template, request, redirect, url_for, abort, flash, jsonify
from io import TextIOWrapper
from .models import (
    load_phonebook,
    add_contact,
    delete_contact,
    update_contact,
    import_contacts,
    import_contacts_xml,
)
from .utils import validate_contact

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    contacts = load_phonebook()
    return render_template('index.html', contacts=contacts)


@main_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form.get('name')
        telephone = request.form.get('telephone')
        if validate_contact(name, telephone):
            add_contact(name, telephone)
            return redirect(url_for('main.index'))
    return render_template('add.html')


@main_bp.route('/delete/<int:index>', methods=['POST', 'DELETE'])
def delete(index):
    success = delete_contact(index)
    if request.method == 'POST':
        return redirect(url_for('main.index'))
    if success:
        return ('', 204)
    return jsonify({'error': 'Not found'}), 404


@main_bp.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
    contacts = load_phonebook()
    if not (0 <= index < len(contacts)):
        abort(404)
    if request.method == 'POST':
        name = request.form.get('name')
        telephone = request.form.get('telephone')
        if validate_contact(name, telephone):
            update_contact(index, name, telephone)
            return redirect(url_for('main.index'))
    contact = contacts[index]
    return render_template('edit.html', contact=contact, index=index)


@main_bp.route('/import', methods=['GET', 'POST'])
def import_view():
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            if file.filename.lower().endswith('.xml'):
                count = import_contacts_xml(file.stream, validate_contact)
            else:
                text_file = TextIOWrapper(file.stream, encoding='utf-8')
                count = import_contacts(text_file, validate_contact)
            if count:
                flash(f"{count} contacten ge\u00efmporteerd.", "info")
            return redirect(url_for('main.index'))
        flash('Geen bestand ge\u00fcppload.', 'error')
    return render_template('import.html')
