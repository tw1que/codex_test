from flask import Flask, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os

from .routes import main_bp
from .routes_xml import xml_bp
from .routes_api import api_bp
from .routes_export import export_bp
from .models import Base, Contact, import_contacts_xml
from .utils import PHONE_RE

def create_app(test_config=None):
    app = Flask(__name__)
    default_db = Path(__file__).resolve().parents[1] / "phonebook.db"
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DATABASE_URI', f'sqlite:///{default_db}'),
        INITIAL_PHONEBOOK_XML=os.environ.get('INITIAL_PHONEBOOK_XML', '/data/phonebook.xml'),
    )

    if test_config:
        app.config.update(test_config)

    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    app.config['SESSION_FACTORY'] = Session
    Base.metadata.create_all(engine)
    app.config['DB_PATH'] = Path(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///',''))

    # perform auto-import from Yealink XML if DB is empty
    def _needs_import(session):
        return session.query(Contact).count() == 0

    session = Session()
    if _needs_import(session):
        xml_path = Path(app.config.get("INITIAL_PHONEBOOK_XML", "/data/phonebook.xml"))
        if xml_path.is_file():
            def _validator(name, telephone):
                if not name or not telephone:
                    return False
                if not PHONE_RE.match(telephone):
                    return False
                digits = telephone.replace(" ", "").lstrip("+")
                return digits.isdigit() and len(digits) <= 15

            with xml_path.open("r", encoding="utf-8") as fh:
                with app.app_context():
                    import_contacts_xml(fh, _validator)
    session.close()

    app.register_blueprint(main_bp)
    app.register_blueprint(xml_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(export_bp)

    @app.route("/health", methods=["GET"])
    def health():
        return Response("OK", status=200, mimetype="text/plain")

    return app
