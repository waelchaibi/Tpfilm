import csv
from services.database_service import get_db
from models.movie import movie

class movieService:

    def create_movie_table(self):
        db = get_db()
        db.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            movie_id TEXT PRIMARY KEY,
            title TEXT,
            content_type TEXT,
            genre_primary TEXT,
            genre_secondary TEXT,
            release_year INTEGER,
            duration_minutes REAL,
            rating TEXT,
            language TEXT,
            country_of_origin TEXT,
            imdb_rating REAL,
            production_budget REAL,
            box_office_revenue REAL,
            number_of_seasons INTEGER,
            number_of_episodes INTEGER,
            is_netflix_original INTEGER,
            added_to_platform TEXT,
            content_warning INTEGER,
            poster TEXT
        )
        """)
        db.commit()
        print("Movies table created.")

    def seed_movies_from_csv(self, csv_path):
        db = get_db()

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:

                db.execute("""
                    INSERT INTO movies (
                        movie_id, title, content_type, genre_primary, genre_secondary,
                        release_year, duration_minutes, rating, language, country_of_origin,
                        imdb_rating, production_budget, box_office_revenue,
                        number_of_seasons, number_of_episodes, is_netflix_original,
                        added_to_platform, content_warning, poster
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(movie_id) DO UPDATE SET
                        title=excluded.title,
                        content_type=excluded.content_type,
                        genre_primary=excluded.genre_primary,
                        genre_secondary=excluded.genre_secondary,
                        release_year=excluded.release_year,
                        duration_minutes=excluded.duration_minutes,
                        rating=excluded.rating,
                        language=excluded.language,
                        country_of_origin=excluded.country_of_origin,
                        imdb_rating=excluded.imdb_rating,
                        production_budget=excluded.production_budget,
                        box_office_revenue=excluded.box_office_revenue,
                        number_of_seasons=excluded.number_of_seasons,
                        number_of_episodes=excluded.number_of_episodes,
                        is_netflix_original=excluded.is_netflix_original,
                        added_to_platform=excluded.added_to_platform,
                        content_warning=excluded.content_warning,
                        poster=excluded.poster
                """, (
                    row['movie_id'],
                    row['title'],
                    row['content_type'],
                    row['genre_primary'],
                    row['genre_secondary'] or None,
                    int(row['release_year']) if row['release_year'] else None,
                    float(row['duration_minutes']) if row['duration_minutes'] else None,
                    row['rating'] or None,
                    row['language'] or None,
                    row['country_of_origin'] or None,
                    float(row['imdb_rating']) if row['imdb_rating'] else None,
                    float(row['production_budget']) if row['production_budget'] else None,
                    float(row['box_office_revenue']) if row['box_office_revenue'] else None,
                    int(float(row['number_of_seasons'])) if row['number_of_seasons'] else None,
                    int(float(row['number_of_episodes'])) if row['number_of_episodes'] else None,
                    1 if row['is_netflix_original'] == "True" else 0,
                    row['added_to_platform'] or None,
                    1 if row['content_warning'] == "True" else 0,
                    ""
                ))

        db.commit()
        
        print(f"Seeded movies from {csv_path}.")
    
    def get_movies_paginated(self, page: int = 1, page_size: int = 20):
        db = get_db()

        offset = (page - 1) * page_size

        rows = db.execute("""
            SELECT
                movie_id, title, content_type, genre_primary, genre_secondary,
                release_year, duration_minutes, rating, language, country_of_origin,
                imdb_rating, production_budget, box_office_revenue,
                number_of_seasons, number_of_episodes, is_netflix_original,
                added_to_platform, content_warning
            FROM movies
            ORDER BY title ASC
            LIMIT ? OFFSET ?
        """, (page_size, offset)).fetchall()

        movies = []
        for r in rows:
            m = movie(
                movie_id=r["movie_id"],
                title=r["title"],
                content_type=r["content_type"],
                genre_primary=r["genre_primary"],
                genre_secondary=r["genre_secondary"],
                release_year=r["release_year"],
                duration_minutes=r["duration_minutes"],
                rating=r["rating"],
                language=r["language"],
                country_of_origin=r["country_of_origin"],
                imdb_rating=r["imdb_rating"],
                production_budget=r["production_budget"],
                box_office_revenue=r["box_office_revenue"],
                number_of_seasons=r["number_of_seasons"],
                number_of_episodes=r["number_of_episodes"],
                is_netflix_original=bool(r["is_netflix_original"]),
                added_to_platform=r["added_to_platform"],
                content_warning=bool(r["content_warning"])
            )
            movies.append(m)

        return movies
