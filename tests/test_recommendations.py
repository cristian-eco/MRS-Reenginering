import pytest
from unittest.mock import patch

# 1. Carga de la vista principal HTML
def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'CineMatch' in response.data

# 2. Endpoint del catálogo (/catalog)
def test_get_catalog_endpoint(client):
    response = client.get('/catalog')
    assert response.status_code == 200
    assert isinstance(response.json, list)

# 3. Endpoint del carrete horizontal (/featured)
def test_get_featured_endpoint(client):
    response = client.get('/featured')
    assert response.status_code == 200
    assert isinstance(response.json, list)

# 4. Exclusión de IDs en /featured
def test_get_featured_with_exclude(client):
    response = client.get('/featured?exclude=550,155')
    assert response.status_code == 200
    assert isinstance(response.json, list)

# 5. Recomendaciones filtradas por género
def test_recommendations_by_genre(client):
    response = client.get('/recommendations?genre=Action&n=5')
    assert response.status_code == 200
    assert isinstance(response.json, list)

# 6. Detalle de película válido (/movie/<id>)
@patch('app.routes.recommendations.fetch_movie_data')
def test_get_movie_details_success(mock_fetch, client):
    mock_fetch.return_value = {
        'id': 550,
        'title': 'Fight Club',
        'vote_average': 8.4,
        'overview': 'Test overview...'
    }
    response = client.get('/movie/550')
    assert response.status_code == 200
    assert response.json['title'] == 'Fight Club'

# 7. Detalle de película no encontrada (404)
@patch('app.routes.recommendations.fetch_movie_data')
def test_get_movie_details_not_found(mock_fetch, client):
    mock_fetch.return_value = None
    response = client.get('/movie/99999999')
    assert response.status_code == 404
    assert 'error' in response.json

# 8. Comportamiento de error 404 global
def test_404_error_handler(client):
    response = client.get('/ruta-inexistente-123')
    assert response.status_code == 404

# 9. Recomendación por calificación mínima
def test_recommendations_with_min_rating(client):
    response = client.get('/recommendations?min_rating=8.0&n=5')
    assert response.status_code == 200
    assert isinstance(response.json, list)

# 10. Recomendación por rango de años
def test_recommendations_with_years(client):
    response = client.get('/recommendations?start_year=2000&end_year=2010&n=5')
    assert response.status_code == 200
    assert isinstance(response.json, list)

# 11. Forzar error en fetch_movie_data (ruta de error en rutas)
@patch('app.routes.recommendations.fetch_movie_data', return_value=None)
def test_movie_details_error_path(mock_fetch, client):
    response = client.get('/movie/123')
    assert response.status_code == 404

# 12. Validar búsqueda con resultados vacíos (bloque if not search_results)
@patch('app.routes.recommendations.search_movies', return_value=[])
def test_search_movies_empty_results(mock_search, client):
    response = client.get('/recommendations?title=PeliculaInexistente')
    assert response.status_code == 200
    assert response.json == []

# 24. Probar búsqueda por título cuando TMDB devuelve lista vacía
@patch('app.routes.recommendations.search_movies')
def test_recommendations_by_title_empty(mock_search, client):
    mock_search.return_value = []
    response = client.get('/recommendations?title=PeliculaQueNoExiste12345')
    assert response.status_code == 200
    assert response.json == []

# 25. Probar endpoint de catálogo (/catalog) cuando ocurre una excepción interna
@patch('app.routes.recommendations.get_recommendations', side_effect=Exception("Database error"))
def test_get_catalog_exception(mock_rec, client):
    response = client.get('/catalog')
    assert response.status_code == 500
    assert response.json == []

# 26. Probar endpoint del carrete (/featured) cuando ocurre una excepción interna
@patch('app.routes.recommendations.get_recommendations', side_effect=Exception("Database error"))
def test_get_featured_exception(mock_rec, client):
    response = client.get('/featured')
    assert response.status_code == 500
    assert response.json == []