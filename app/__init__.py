from flask import Flask
from .routes import main_bp

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
        PHONEBOOK_PATH='phonebook.xml'
    )

    if test_config:
        app.config.update(test_config)

    app.register_blueprint(main_bp)
    return app
