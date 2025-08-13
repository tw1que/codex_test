from flask import Flask, Response
from pathlib import Path
import xml.etree.ElementTree as ET
import click
from .routes import main_bp
from .models import db, init_db, Contact

def create_app(test_config=None):
    app = Flask(__name__)
    base_path = Path(__file__).resolve().parents[1]
    default_phonebook = base_path / "phonebook.xml"
    default_db = base_path / "phonebook.db"
    app.config.from_mapping(
        SECRET_KEY='dev',
        PHONEBOOK_PATH=str(default_phonebook),
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{default_db}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    app.register_blueprint(main_bp)

    @app.cli.command("init-db")
    def init_db_command():
        """Initialize the database and import contacts from phonebook.xml."""
        init_db()
        click.echo("Initialized the database.")

    @app.route("/health", methods=["GET"])
    def health():
        return Response("OK", status=200, mimetype="text/plain")

    @app.route("/phonebook.xml", methods=["GET"])
    def serve_phonebook():
        contacts = Contact.query.order_by(Contact.name).all()
        root = ET.Element('YealinkIPPhoneDirectory')
        for c in contacts:
            entry = ET.SubElement(root, 'DirectoryEntry')
            ET.SubElement(entry, 'Name').text = c.name
            ET.SubElement(entry, 'Telephone').text = c.telephone
        xml_data = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        return Response(xml_data, mimetype='application/xml')

    return app
