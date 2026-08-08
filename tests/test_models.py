import pytest
from run import app
from app.routes.recommendations import fetch_movie_data, search_movies
from app.models.movie import Movie

# 13. Método estático Movie.get_all()
def test_movie_model_get_all():
    with app.app_context():
        movies = Movie.get_all()
        assert isinstance(movies, list)
        if len(movies) > 0:
            assert hasattr(movies[0], 'title')

# 14. Método estático Movie.get_movies_by_genre()
def test_movie_model_by_genre():
    with app.app_context():
        movies = Movie.get_movies_by_genre('Comedy')
        assert isinstance(movies, list)

# 15. Método estático Movie.get_movie_details()
def test_movie_model_details():
    with app.app_context():
        movie = Movie.get_movie_details(1)
        assert movie is None or isinstance(movie, Movie)

# 16. Fallback de red en fetch_movie_data
def test_fetch_movie_data_failure():
    data = fetch_movie_data(-1)
    assert data is None

# 17. Búsqueda de películas vacía en API externa
def test_search_movies_empty():
    results = search_movies("")
    assert isinstance(results, list)