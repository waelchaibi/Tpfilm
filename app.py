from flask import Flask
import os
from routes import main
from services.database_service import get_db


def create_app():
    app = Flask(__name__)
    app.register_blueprint(main.bp)

    from services.database_service import get_db, init_app
    init_app(app)
    
    with app.app_context():
        db = get_db()
        row = db.execute("SELECT datetime('now') AS utc_time").fetchone()
        print({"utc_time": row["utc_time"]})

    return app

app = create_app()

if __name__ == "__main__":
    # Read environment variables
    env = os.getenv("FLASK_ENV", "production")
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))

    debug = env == "development"

    app.run(host=host, port=port, debug=debug)