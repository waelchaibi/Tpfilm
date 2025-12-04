class movie:
    def __init__(self, show_id, type, title, director, cast, country, 
                 date_added, release_year, rating, duration, listed_in, 
                 description,
                 imdb_rating=None, imdb_votes=None, runtime=None, 
                 genre=None, language=None, awards=None, box_office=None,
                 poster=None, production=None, website=None,
                 last_updated=None, omdb_data_available=False):
        
        self.show_id = show_id
        self.type = type
        self.title = title
        self.director = director
        self.cast = cast
        self.country = country
        self.date_added = date_added
        self.release_year = release_year
        self.rating = rating
        self.duration = duration
        self.listed_in = listed_in
        self.description = description
        
        self.imdb_rating = imdb_rating
        self.imdb_votes = imdb_votes
        self.runtime = runtime
        self.genre = genre
        self.language = language
        self.awards = awards
        self.box_office = box_office
        self.poster = poster
        self.production = production
        self.website = website
        
        self.last_updated = last_updated
        self.omdb_data_available = omdb_data_available