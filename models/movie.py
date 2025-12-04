class movie:
    def __init__(self, movie_id, title, content_type, genre_primary,
                 genre_secondary=None, release_year=None, duration_minutes=None,
                 rating=None, language=None, country_of_origin=None,
                 imdb_rating=None, production_budget=None, box_office_revenue=None,
                 number_of_seasons=None, number_of_episodes=None,
                 is_netflix_original=False, added_to_platform=None,
                 content_warning=False, poster=None):
        self.movie_id = movie_id
        self.title = title
        self.content_type = content_type
        self.genre_primary = genre_primary
        self.genre_secondary = genre_secondary
        self.release_year = release_year
        self.duration_minutes = duration_minutes
        self.rating = rating
        self.language = language
        self.country_of_origin = country_of_origin
        self.imdb_rating = imdb_rating
        self.production_budget = production_budget
        self.box_office_revenue = box_office_revenue
        self.number_of_seasons = number_of_seasons
        self.number_of_episodes = number_of_episodes
        self.is_netflix_original = is_netflix_original
        self.added_to_platform = added_to_platform
        self.content_warning = content_warning
        self.poster = poster