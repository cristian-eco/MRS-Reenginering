"""
Fachada de servicios de recomendación.

Refactorizado para delegar en el patrón Strategy (ver `app/services/strategies.py`).
Las funciones públicas mantienen el mismo nombre y comportamiento externo que la
versión original, para no romper las rutas existentes (`app/routes/recommendations.py`).
"""

import logging

from app.services.strategies import DemographicStrategy, ContentBasedStrategy

logging.basicConfig(level=logging.INFO)

# Las estrategias se instancian una sola vez al cargar el módulo, ya que
# ContentBasedStrategy prepara datos costosos (TF-IDF, merge de dataframes)
# durante su inicialización.
_demographic_strategy = DemographicStrategy()
_content_based_strategy = ContentBasedStrategy()


def get_recommendations(genre=None, n=10, min_rating=0, start_year=None, end_year=None):
    """
    Recomendaciones vía filtrado demográfico.

    Nota: acepta start_year/end_year para ser compatible con la firma que
    espera `app/routes/recommendations.py::get_recommendations_by_criteria`,
    resolviendo el TypeError documentado en el README (errores solucionados, #5).
    """
    recommendations = _demographic_strategy.recommend(
        genre=genre, n=n, min_rating=min_rating, start_year=start_year, end_year=end_year
    )
    logging.info(f"Returning {len(recommendations)} recommendations (demographic strategy)")
    return recommendations


def get_content_based_recommendations(title, n=10):
    """Recomendaciones vía filtrado basado en contenido (similitud de coseno)."""
    recommendations = _content_based_strategy.recommend(title=title, n=n)
    logging.info(f"Returning {len(recommendations)} recommendations (content-based strategy)")
    return recommendations