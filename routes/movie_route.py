from flask import Blueprint, render_template, request
from services.movie_service import movieService

bp = Blueprint('movie', __name__)

@bp.route('/movies')
def movies():
    service = movieService()
    page_size = 20
    page_arg = request.args.get('page', '1')
    try:
        page = int(page_arg)
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    movies_fetched = service.get_movies_paginated(page=page, page_size=page_size + 1)

    has_next = len(movies_fetched) > page_size
    movies = movies_fetched[:page_size]  # show only page_size items

    return render_template(
        "movies.html",
        movies=movies,
        page=page,
        has_next=has_next
    )
