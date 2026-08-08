import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    DATABASE_PATH = os.path.join(BASE_DIR, '..', 'data', 'movies.db')
    MOVIES_METADATA_PATH = os.path.join(BASE_DIR, '..', 'data', 'tmdb_5000_movies.csv')
    CREDITS_PATH = os.path.join(BASE_DIR, '..', 'data', 'tmdb_5000_credits.csv')

    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
    TMDB_BASE_URL = os.getenv(
        "TMDB_BASE_URL",
        "https://api.themoviedb.org/3"
    )