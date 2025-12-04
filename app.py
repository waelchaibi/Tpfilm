from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager, current_user
import os
from routes import main, users
from routes.movie_route import create_movie_blueprint
from services.database_service import get_db
from services.user_service import get_user_by_id
from services.movie_service import movieService


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "n'importe")
    app.register_blueprint(main.bp)
    
    app.register_blueprint(users.bp)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'users.login'

    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            return get_user_by_id(int(user_id))
        except Exception:
            return None

    from services.database_service import get_db, init_app
    from models.users import initialize_users_table
    init_app(app)
    
    
    with app.app_context():
        db = get_db()
        initialize_users_table()
        row = db.execute("SELECT datetime('now') AS utc_time").fetchone()
        print({"utc_time": row["utc_time"]})
        movie_service = movieService(os.getenv("MOVIE_SERVICE_API_KEY"))
        movie_service.create_movie_table()
        movie_service.seed_movies_from_csv('./data/netflix_titles.csv')
    
        app.register_blueprint(create_movie_blueprint(movie_service))
    return app

app = create_app()

if __name__ == "__main__":
    # Read environment variables
    env = os.getenv("FLASK_ENV", "production")
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))

    debug = env == "development"

    app.run(host=host, port=port, debug=debug)