from flask import Blueprint, jsonify, request, render_template
import requests
import random
from app.services.recommendation_service import get_recommendations, get_content_based_recommendations
from config.config import Config
from app.models.movie import Movie

bp = Blueprint('recommendations', __name__)

import random

@bp.route('/featured')
def get_featured_strip():
    """
    Obtiene películas aleatorias de alta calificación para el carrete horizontal,
    asegurando que cambien dinámicamente y evitando duplicados con el catálogo.
    """
    try:
        # 1. Obtener lista de IDs a excluir (enviados desde el frontend como ?exclude=1,2,3)
        exclude_raw = request.args.get('exclude', '')
        exclude_ids = set(int(x) for x in exclude_raw.split(',') if x.isdigit())

        # 2. Obtener un conjunto amplio de buenas películas (ej. min_rating 7.0)
        candidates = get_recommendations(genre="", n=60, min_rating=7.0)
        
        # 3. Filtrar las que no estén en la lista de exclusión
        available_movies = [m for m in candidates if m.id not in exclude_ids]

        # Si no quedan suficientes tras la exclusión, usamos las candidatas normales
        if len(available_movies) < 8:
            available_movies = candidates

        # 4. Seleccionar 8 películas aleatorias en cada petición
        selected_movies = random.sample(available_movies, min(len(available_movies), 8))
        
        featured_list = []
        for movie in selected_movies:
            movie_data = process_movie_from_db(movie)
            if movie_data and movie_data.get('poster_path'):
                featured_list.append(movie_data)
                
        return jsonify(featured_list)
    except Exception as e:
        print(f"Error al obtener películas destacadas dinámicas: {e}")
        return jsonify([]), 500

@bp.route("/catalog")
def get_catalog():
    """
    Devuelve un catálogo inicial más variado mezclando géneros
    y selecciones aleatorias de la base de datos.
    """
    try:
        # Obtenemos un grupo más amplio de películas (ej. 80 candidatas) con rating aceptable (>= 6.0)
        candidates = get_recommendations(genre="", n=80, min_rating=6.0)
        
        # Seleccionamos 24 de forma aleatoria en cada carga/recarga
        if len(candidates) >= 24:
            selected_movies = random.sample(candidates, 24)
        else:
            selected_movies = candidates

        return jsonify([
            process_movie_from_db(movie)
            for movie in selected_movies
        ])
    except Exception as e:
        print(f"Error cargando catálogo variado: {e}")
        return jsonify([]), 500

def fetch_movie_data(movie_id):
    url = f"{Config.TMDB_BASE_URL}/movie/{movie_id}?api_key={Config.TMDB_API_KEY}&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching movie data: {e}")
        return None

def search_movies(query):
    url = f"{Config.TMDB_BASE_URL}/search/movie?api_key={Config.TMDB_API_KEY}&language=en-US&query={query}&page=1&include_adult=false"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()['results']
    except requests.RequestException as e:
        print(f"Error searching movies: {e}")
        return []

def get_tmdb_recommendations(movie_id, n):
    url = f"{Config.TMDB_BASE_URL}/movie/{movie_id}/recommendations?api_key={Config.TMDB_API_KEY}&language=en-US&page=1"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()['results'][:n]
    except requests.RequestException as e:
        print(f"Error getting TMDB recommendations: {e}")
        return []

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/recommendations')
def get_movie_recommendations():
    genre = request.args.get('genre', '')
    n = request.args.get('n', default=10, type=int)
    start_year = request.args.get('start_year', type=int)
    end_year = request.args.get('end_year', type=int)
    min_rating = request.args.get('min_rating', default=0, type=float)
    title = request.args.get('title', '')

    if title:
        recommendations = get_recommendations_by_title(title, n, genre, min_rating)
    else:
        recommendations = get_recommendations_by_criteria(genre, n, start_year, end_year, min_rating)

    return jsonify(recommendations)

def get_recommendations_by_title(title, n, genre, min_rating):
    search_results = search_movies(title)
    if not search_results:
        return []

    movie_id = search_results[0]['id']
    tmdb_recommendations = get_tmdb_recommendations(movie_id, n)
    return [movie for movie in (process_movie(m, genre, min_rating) for m in tmdb_recommendations) if movie]

def get_recommendations_by_criteria(genre, n, start_year, end_year, min_rating):
    recommendations = get_recommendations(genre, n, start_year, end_year, min_rating)
    return [process_movie_from_db(r) for r in recommendations]

def process_movie(movie, genre, min_rating):
    movie_data = fetch_movie_data(movie['id'])
    if not movie_data:
        return None

    movie_genres = [g['name'] for g in movie_data['genres']]
    if (not genre or genre in movie_genres) and movie['vote_average'] >= min_rating:
        return {
            'id': movie['id'],
            'title': movie['title'],
            'poster_path': movie['poster_path'],
            'rating': movie['vote_average'],
            'genres': movie_genres,
            'overview': movie_data.get('overview', 'No overview available.')
        }
    return None

def process_movie_from_db(movie):
    movie_data = fetch_movie_data(movie.id)
    return {
        'id': movie.id,
        'title': movie.title,
        'rating': movie.rating,
        'genres': movie.genres,
        'poster_path': movie_data['poster_path'] if movie_data else None,
        'overview': movie_data.get('overview', 'No overview available.') if movie_data else 'No overview available.'
    }

@bp.route('/movie/<int:movie_id>')
def get_movie_details(movie_id):
    movie_data = fetch_movie_data(movie_id)
    if movie_data:
        return jsonify(movie_data)
    return jsonify({'error': 'Movie not found'}), 404

@bp.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500