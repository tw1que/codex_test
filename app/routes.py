from flask import Blueprint, current_app, render_template, request, redirect, url_for
from .models import load_phonebook, add_contact, delete_contact
from .utils import validate_contact

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    contacts = load_phonebook(current_app.config['PHONEBOOK_PATH'])
    return render_template('index.html', contacts=contacts)


@main_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form.get('name')
        telephone = request.form.get('telephone')
        label = request.form.get('label', '')
        if validate_contact(name, telephone):
            add_contact(current_app.config['PHONEBOOK_PATH'], name, telephone, label)
            return redirect(url_for('main.index'))
    return render_template('add.html')


@main_bp.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    delete_contact(current_app.config['PHONEBOOK_PATH'], index)
    return redirect(url_for('main.index'))
