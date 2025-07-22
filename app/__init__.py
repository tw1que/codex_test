from flask import Flask, send_file, current_app
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

    @app.route("/health", methods=["GET"])
    def health():
        return "OK", 200

    @app.route("/phonebook.xml", methods=["GET"])
    def serve_phonebook():
        """
        Serve the phonebook XML file from the configured path.
        """
        return send_file(
            current_app.config["PHONEBOOK_PATH"],
            mimetype="application/xml",
            as_attachment=False,
        )

    return app
