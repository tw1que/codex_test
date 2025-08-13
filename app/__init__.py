from flask import Flask, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import xml.etree.ElementTree as ET
from pathlib import Path

from .routes import main_bp
from .models import Base, Contact

def create_app(test_config=None):
    app = Flask(__name__)
    default_db = Path(__file__).resolve().parents[1] / "phonebook.db"
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{default_db}'
    )

    if test_config:
        app.config.update(test_config)

    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    app.config['SESSION_FACTORY'] = Session
    Base.metadata.create_all(engine)

    app.register_blueprint(main_bp)

    @app.route("/health", methods=["GET"])
    def health():
        return Response("OK", status=200, mimetype="text/plain")

    @app.route("/phonebook.xml", methods=["GET"])
    def serve_phonebook():
        """Generate and return the phonebook XML from the database."""
        session = app.config['SESSION_FACTORY']()
        contacts = session.query(Contact).order_by(Contact.name).all()
        root = ET.Element('YealinkIPPhoneDirectory')
        for c in contacts:
            entry = ET.SubElement(root, 'DirectoryEntry')
            ET.SubElement(entry, 'Name').text = c.name
            ET.SubElement(entry, 'Telephone').text = c.telephone
        session.close()
        xml_bytes = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        return Response(xml_bytes, mimetype='application/xml')

    return app
