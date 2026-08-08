"""
Implementación del patrón de diseño Strategy para los motores de recomendación.

Cada motor de recomendación (demográfico y basado en contenido) implementa una
interfaz común (`RecommendationStrategy`), lo que permite:
- Añadir nuevos motores de recomendación sin modificar el código existente.
- Eliminar la inconsistencia de firmas entre `recommendation_service.py`
y las rutas que lo consumen (bug documentado en el README, sección de
errores solucionados, punto 5).
"""

from abc import ABC, abstractmethod
import logging

from app.data_processing.demographic_filtering import get_top_movies
from app.data_processing.content_based_filtering import (
    prepare_content_based_data,
    get_recommendations as get_content_recommendations,
)
from app.models.movie import Movie

logging.basicConfig(level=logging.INFO)


class RecommendationStrategy(ABC):
    """Interfaz común que deben implementar todos los motores de recomendación."""

    @abstractmethod
    def recommend(self, **kwargs):
        """Devuelve una lista de instancias de `Movie` según el criterio del motor."""
        raise NotImplementedError


class DemographicStrategy(RecommendationStrategy):
    """
    Motor de filtrado demográfico: recomienda las películas mejor calificadas
    usando el weighted rating de IMDB, con filtros opcionales de género y
    calificación mínima.
    """

    def recommend(self, genre=None, n=10, min_rating=0, start_year=None, end_year=None):
        top_movies = get_top_movies(n * 2)
        logging.info(f"[Demographic] Retrieved {len(top_movies)} top movies")

        if top_movies.empty:
            logging.warning("[Demographic] No top movies retrieved")
            return []

        recommendations = [
            Movie(
                id=row['id'],
                title=row['title'],
                genres=row.get('genres', ''),
                rating=row.get('vote_average', 0)
            )
            for _, row in top_movies.iterrows()
        ]

        if genre:
            recommendations = [
                movie for movie in recommendations
                if genre.lower() in movie.genres.lower()
            ]
            logging.info(f"[Demographic] {len(recommendations)} movies after genre filter")

        if min_rating:
            recommendations = [movie for movie in recommendations if movie.rating >= min_rating]
            logging.info(f"[Demographic] {len(recommendations)} movies after rating filter")

        # NOTA: start_year / end_year aún no filtran, porque load_and_process_data()
        # no incluye release_date en el dataframe demográfico. Queda documentado
        # como mejora pendiente para no romper la interfaz de la ruta mientras tanto.

        recommendations.sort(key=lambda x: x.rating, reverse=True)
        final_recommendations = recommendations[:n]
        logging.info(f"[Demographic] Returning {len(final_recommendations)} recommendations")

        if not final_recommendations:
            logging.warning("[Demographic] No recommendations found, returning top rated movies")
            return [
                Movie(id=row['id'], title=row['title'], genres=row.get('genres', ''), rating=row.get('vote_average', 0))
                for _, row in top_movies.head(n).iterrows()
            ]

        return final_recommendations


class ContentBasedStrategy(RecommendationStrategy):
    """
    Motor de filtrado basado en contenido: recomienda películas similares a un
    título dado usando TF-IDF + similitud de coseno sobre sinopsis, reparto,
    director, palabras clave y género.
    """

    def __init__(self):
        # Se prepara una sola vez al instanciar la estrategia (costoso: TF-IDF + merge).
        self.df, self.cosine_sim, self.indices = prepare_content_based_data()

    def recommend(self, title=None, n=10, **kwargs):
        if not title:
            logging.warning("[ContentBased] Se requiere un 'title' para este motor")
            return []

        content_recommendations = get_content_recommendations(title, self.df, self.cosine_sim, self.indices)
        logging.info(f"[ContentBased] Retrieved {len(content_recommendations)} recommendations")

        if content_recommendations.empty:
            logging.warning(f"[ContentBased] No recommendations found for '{title}'")
            return []

        recommendations = [
            Movie(
                id=self.df.loc[idx, 'id'],
                title=self.df.loc[idx, 'title'],
                genres=self.df.loc[idx, 'genres'],
                rating=self.df.loc[idx, 'vote_average']
            )
            for idx in content_recommendations.index[:n]
            if idx in self.df.index
        ]

        logging.info(f"[ContentBased] Returning {len(recommendations)} recommendations")
        return recommendations