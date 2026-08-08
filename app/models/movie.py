from app.utils.database import get_db

class Movie:
    def __init__(self, id, title, genres, rating=0.0, poster_path=None):
        self.id = id
        self.title = title
        self.genres = genres
        self.rating = rating
        self.poster_path = poster_path

    @staticmethod
    def get_all(limit=20):
        db = get_db()
        cursor = db.cursor()
        # Omitimos la columna de calificación para evitar el OperationalError
        cursor.execute("SELECT id, title, genres FROM movies LIMIT ?", (limit,))
        return [Movie(row[0], row[1], row[2], 0.0) for row in cursor.fetchall()]

    @staticmethod
    def get_movies_by_genre(genre, limit=20):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, title, genres FROM movies WHERE genres LIKE ? LIMIT ?", (f'%{genre}%', limit))
        return [Movie(row[0], row[1], row[2], 0.0) for row in cursor.fetchall()]

    @staticmethod
    def get_movie_details(movie_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, title, genres FROM movies WHERE id = ?", (movie_id,))
        row = cursor.fetchone()
        if row:
            return Movie(row[0], row[1], row[2], 0.0)
        return None

    @staticmethod
    def get_featured_movies(limit=8):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, title, genres FROM movies ORDER BY RANDOM() LIMIT ?", (limit,))
        # Devolvemos una tupla de 4 elementos simulando el rating para la ruta /featured
        return [(row[0], row[1], row[2], 0.0) for row in cursor.fetchall()]