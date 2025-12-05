import csv
import requests
from datetime import datetime
from services.database_service import get_db
from models.movie import movie

class movieService:
    def __init__(self, omdb_api_key: str):
        self.omdb_api_key = omdb_api_key
        self.base_omdb_url = "http://www.omdbapi.com/"
    
    def create_movie_table(self) -> None:
        db = get_db()
        db.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            show_id TEXT PRIMARY KEY, type TEXT, title TEXT, director TEXT,
            cast TEXT, country TEXT, date_added TEXT, release_year INTEGER,
            rating TEXT, duration TEXT, listed_in TEXT, description TEXT,
            imdb_rating REAL, imdb_votes TEXT, runtime TEXT, genre TEXT,
            language TEXT, awards TEXT, box_office TEXT, poster TEXT,
            production TEXT, website TEXT, last_updated TEXT,
            omdb_data_available INTEGER DEFAULT 0, omdb_last_attempt TEXT
        )
        """)
        db.commit()
    
    def seed_movies_from_csv(self, csv_path: str) -> None:
        db = get_db()
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if not row.get('show_id') or not row.get('title'):
                    continue
                
                release_year = int(row['release_year']) if row['release_year'] and row['release_year'].isdigit() else None
                
                db.execute("""
                    INSERT OR IGNORE INTO movies (
                        show_id, type, title, director, cast, country,
                        date_added, release_year, rating, duration, listed_in, description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['show_id'], row['type'], row['title'],
                    row['director'] or None, row['cast'] or None, row['country'] or None,
                    row['date_added'] or None, release_year, row['rating'] or None,
                    row['duration'] or None, row['listed_in'] or None, row['description'] or None
                ))
        db.commit()
    
    def fetch_omdb_data(self, title: str, year: int = None) -> dict:
        params = {'t': title, 'apikey': self.omdb_api_key, 'r': 'json'}
        if year:
            params['y'] = year
        
        try:
            response = requests.get(self.base_omdb_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('Response') == 'True':
                    return {
                        'imdb_rating': float(data.get('imdbRating', 0)) if data.get('imdbRating') not in [None, 'N/A'] else None,
                        'imdb_votes': data.get('imdbVotes', '').replace(',', '') if data.get('imdbVotes') != 'N/A' else None,
                        'runtime': data.get('Runtime') if data.get('Runtime') != 'N/A' else None,
                        'genre': data.get('Genre') if data.get('Genre') != 'N/A' else None,
                        'language': data.get('Language') if data.get('Language') != 'N/A' else None,
                        'awards': data.get('Awards') if data.get('Awards') != 'N/A' else None,
                        'box_office': data.get('BoxOffice') if data.get('BoxOffice') != 'N/A' else None,
                        'poster': data.get('Poster') if data.get('Poster') != 'N/A' else None,
                        'production': data.get('Production') if data.get('Production') != 'N/A' else None,
                        'website': data.get('Website') if data.get('Website') != 'N/A' else None,
                        'success': True
                    }
            return {'success': False, 'error': 'Movie not found or API error'}
        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}
    
    def consolidate_movie(self, movie_id: str, force_refresh: bool = False) -> tuple[bool, str]:
        db = get_db()
        movie_data = db.execute(
            "SELECT title, release_year, omdb_data_available, omdb_last_attempt FROM movies WHERE show_id = ?",
            (movie_id,)
        ).fetchone()
        
        if not movie_data:
            return False, "Movie not found"
        
        if not force_refresh:
            if movie_data['omdb_data_available']:
                return True, "Already consolidated"
            if movie_data['omdb_last_attempt']:
                last_attempt = datetime.strptime(movie_data['omdb_last_attempt'], '%Y-%m-%d %H:%M:%S')
                if (datetime.now() - last_attempt).days < 7:
                    return False, "Attempted recently"
        
        omdb_data = self.fetch_omdb_data(movie_data['title'], movie_data['release_year'])
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if omdb_data.get('success'):
            db.execute("""
                UPDATE movies SET imdb_rating = ?, imdb_votes = ?, runtime = ?, genre = ?,
                    language = ?, awards = ?, box_office = ?, poster = ?, production = ?, website = ?,
                    last_updated = ?, omdb_data_available = 1, omdb_last_attempt = ?
                WHERE show_id = ?
            """, (
                omdb_data.get('imdb_rating'), omdb_data.get('imdb_votes'), omdb_data.get('runtime'),
                omdb_data.get('genre'), omdb_data.get('language'), omdb_data.get('awards'),
                omdb_data.get('box_office'), omdb_data.get('poster'), omdb_data.get('production'),
                omdb_data.get('website'), now, now, movie_id
            ))
            db.commit()
            return True, "Consolidation successful"
        else:
            if omdb_data.get('error') == 'Movie not found':
                db.execute("DELETE FROM movies WHERE show_id = ?", (movie_id,))
                db.commit()
                return False, "Deleted - OMDB match not found"
            
            db.execute("UPDATE movies SET omdb_last_attempt = ? WHERE show_id = ?", (now, movie_id))
            db.commit()
            return False, f"OMDB error: {omdb_data.get('error', 'Unknown error')}"
    
    def search_movies(self, query: str, page: int = 1, page_size: int = 20, consolidate: bool = True) -> tuple[list[movie], bool]:
        db = get_db()
        offset = (page - 1) * page_size
        search_pattern = f"%{query}%"
        
        rows = db.execute(
            "SELECT * FROM movies WHERE title LIKE ? ORDER BY title ASC LIMIT ? OFFSET ?",
            (search_pattern, page_size, offset)
        ).fetchall()
        
        movies = []
        for r in rows:
            if consolidate:
                self.consolidate_movie(r['show_id'])
                r = db.execute("SELECT * FROM movies WHERE show_id = ?", (r['show_id'],)).fetchone()
            
            movies.append(movie(
                show_id=r['show_id'], type=r['type'], title=r['title'], director=r['director'],
                cast=r['cast'], country=r['country'], date_added=r['date_added'],
                release_year=r['release_year'], rating=r['rating'], duration=r['duration'],
                listed_in=r['listed_in'], description=r['description'],
                imdb_rating=r['imdb_rating'], imdb_votes=r['imdb_votes'], runtime=r['runtime'],
                genre=r['genre'], language=r['language'], awards=r['awards'],
                box_office=r['box_office'], poster=r['poster'], production=r['production'],
                website=r['website'], last_updated=r['last_updated'],
                omdb_data_available=bool(r['omdb_data_available'])
            ))
        
        total = db.execute(
            "SELECT COUNT(*) AS c FROM movies WHERE title LIKE ?",
            (search_pattern,)
        ).fetchone()['c']
        
        return movies, (page * page_size) < total

    def get_movies_paginated(self, page: int = 1, page_size: int = 20, consolidate: bool = True) -> tuple[list[movie], bool]:
        db = get_db()
        offset = (page - 1) * page_size
        rows = db.execute("SELECT * FROM movies ORDER BY title ASC LIMIT ? OFFSET ?", (page_size, offset)).fetchall()
        
        movies = []
        for r in rows:
            if consolidate:
                self.consolidate_movie(r['show_id'])
                r = db.execute("SELECT * FROM movies WHERE show_id = ?", (r['show_id'],)).fetchone()
            
            movies.append(movie(
                show_id=r['show_id'], type=r['type'], title=r['title'], director=r['director'],
                cast=r['cast'], country=r['country'], date_added=r['date_added'],
                release_year=r['release_year'], rating=r['rating'], duration=r['duration'],
                listed_in=r['listed_in'], description=r['description'],
                imdb_rating=r['imdb_rating'], imdb_votes=r['imdb_votes'], runtime=r['runtime'],
                genre=r['genre'], language=r['language'], awards=r['awards'],
                box_office=r['box_office'], poster=r['poster'], production=r['production'],
                website=r['website'], last_updated=r['last_updated'],
                omdb_data_available=bool(r['omdb_data_available'])
            ))
        
        total = db.execute("SELECT COUNT(*) AS c FROM movies").fetchone()['c']
        return movies, (page * page_size) < total
    
    def get_movie_by_id(self, show_id: str) -> movie | None:
        db = get_db()
        self.consolidate_movie(show_id)
        row = db.execute("SELECT * FROM movies WHERE show_id = ?", (show_id,)).fetchone()
        return movie(**{k: row[k] for k in row.keys()}, omdb_data_available=bool(row['omdb_data_available'])) if row else None
    
    def get_consolidation_stats(self) -> dict:
        db = get_db()
        stats = db.execute("""
            SELECT COUNT(*) as total_movies,
                SUM(omdb_data_available) as consolidated_movies,
                AVG(CASE WHEN omdb_data_available = 1 THEN 1 ELSE 0 END) * 100 as consolidation_rate,
                COUNT(CASE WHEN poster IS NOT NULL AND poster != '' THEN 1 END) as movies_with_poster,
                COUNT(CASE WHEN imdb_rating IS NOT NULL THEN 1 END) as movies_with_imdb_rating
            FROM movies
        """).fetchone()
        return dict(stats)
