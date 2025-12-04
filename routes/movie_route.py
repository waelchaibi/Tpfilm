from flask import Blueprint, render_template
from services.movie_service import movieService

bp = Blueprint('movie', __name__)

@bp.route('/movies')
def movies():
    service = movieService()
    movies = service.get_movies_paginated(page=1, page_size=20)
    return render_template("movies.html", movies=movies)