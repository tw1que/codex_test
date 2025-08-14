from flask import Blueprint, render_template, request, redirect, url_for, abort, flash, jsonify
from io import TextIOWrapper
from .models import load_phonebook, add_contact, delete_contact, update_contact, import_contacts
from .utils import validate_contact

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    contacts = load_phonebook()
    indexed = list(enumerate(contacts))
    if q:
        q_lower = q.lower()
        indexed = [
            (i, c)
            for i, c in indexed
            if q_lower in c['name'].lower() or q_lower in c['telephone'].lower()
        ]
    if category:
        indexed = [(i, c) for i, c in indexed if c['category'] == category]
    return render_template('index.html', contacts=indexed, q=q, category=category)


@main_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form.get('name')
        telephone = request.form.get('telephone')
        category = request.form.get('category', 'other')
        if validate_contact(name, telephone):
            add_contact(name, telephone, category)
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
        category = request.form.get('category', 'other')
        if validate_contact(name, telephone):
            update_contact(index, name, telephone, category)
            return redirect(url_for('main.index'))
    contact = contacts[index]
    return render_template('edit.html', contact=contact, index=index)


@main_bp.route('/import', methods=['GET', 'POST'])
def import_view():
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            text_file = TextIOWrapper(file.stream, encoding='utf-8')
            count = import_contacts(text_file, validate_contact)
            if count:
                flash(f"{count} contacten ge\u00efmporteerd.", "info")
            return redirect(url_for('main.index'))
        flash('Geen bestand ge\u00fcppload.', 'error')
    return render_template('import.html')
