from flask import Blueprint, render_template, request

def create_movie_blueprint(movie_service):
    bp = Blueprint('movie', __name__)

    @bp.route('/movies')
    def movies():
        page = request.args.get('page', 1, type=int)

        movies_list, has_next = movie_service.get_movies_paginated(
            page=page,
            page_size=20,
            consolidate=True
        )

        stats = movie_service.get_consolidation_stats()

        return render_template(
            'movies.html',
            movies=movies_list,
            page=page,
            has_next=has_next,
            stats=stats
        )

    return bp
