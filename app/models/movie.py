from app.utils.database import get_db

class Movie:
    def __init__(self, id, title, genres, rating=None):
        self.id = id
        self.title = title
        self.genres = genres
        self.rating = rating

    @staticmethod
    def get_all(limit=20):
        db = get_db()
        cursor = db.cursor()
        # Pedimos únicamente las 20 mejores o las primeras 20
        cursor.execute("SELECT id, title, genres, vote_average FROM movies LIMIT ?", (limit,))
        return [Movie(id, title, genres, rating) for id, title, genres, rating in cursor.fetchall()]
    
    @staticmethod
    def get_movies_by_genre(genre):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, title, genres, vote_average FROM movies WHERE genres LIKE ?", (f'%{genre}%',))
        return [Movie(id, title, genres, rating) for id, title, genres, rating in cursor.fetchall()]

    @staticmethod
    def get_movie_details(movie_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, title, genres, vote_average FROM movies WHERE id = ?", (movie_id,))
        row = cursor.fetchone()
        if row:
            return Movie(*row)
        return None

    @staticmethod
    def get_movies_by_title(title):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, title, genres, vote_average FROM movies WHERE title LIKE ?", (f'%{title}%',))
        return [Movie(id, title, genres, rating) for id, title, genres, rating in cursor.fetchall()]

    @staticmethod
    def get_featured_movies(limit=8):
        db = get_db()
        cursor = db.cursor()
        # Selecciona películas aleatorias para el carrete
        cursor.execute("SELECT id, title, genres, vote_average, poster_path FROM movies ORDER BY RANDOM() LIMIT ?", (limit,))
        return cursor.fetchall()
