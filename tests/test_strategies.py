import pytest
from run import app
from app.services.recommendation_service import get_recommendations

# 18. Probar recomendaciones base/demográficas sin filtros
def test_recommendations_default():
    with app.app_context():
        results = get_recommendations(genre="", n=5)
        assert isinstance(results, list)

# 19. Probar recomendaciones filtradas por año de inicio y fin
def test_recommendations_year_filtering():
    with app.app_context():
        results = get_recommendations(genre="", n=5, start_year=1990, end_year=2000, min_rating=5.0)
        assert isinstance(results, list)

# 20. Probar recomendaciones con género y calificación mínima simultáneamente
def test_recommendations_genre_and_rating():
    with app.app_context():
        results = get_recommendations(genre="Drama", n=5, min_rating=7.5)
        assert isinstance(results, list)

# 21. Probar recomendación cuando se pasa calificación mínima baja
def test_recommendations_low_min_rating():
    with app.app_context():
        results = get_recommendations(genre="Action", n=5, min_rating=3.0)
        assert isinstance(results, list)

# 22. Probar recomendación con género no existente o raro
def test_recommendations_unknown_genre():
    with app.app_context():
        results = get_recommendations(genre="NonExistentGenre123", n=5)
        assert isinstance(results, list)

# 23. Probar límite de resultados (n=1)
def test_recommendations_limit():
    with app.app_context():
        results = get_recommendations(genre="", n=1)
        assert isinstance(results, list)
        assert len(results) <= 1