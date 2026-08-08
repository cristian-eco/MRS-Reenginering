import os
import logging
from ast import literal_eval
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel
from config.config import Config

logging.basicConfig(level=logging.INFO)

def prepare_content_based_data():
    # 1. Cargar metadatos
    df2 = pd.read_csv(Config.MOVIES_METADATA_PATH, low_memory=False)
    # DETECCIÓN DE ENTORNO:
    # Si estamos en Render (donde existe la variable 'RENDER'), aplicamos el límite de 1000 películas.
    # En tu computadora local (donde NO existe la variable 'RENDER'), se procesan las 4,803 películas completas.
    is_render = os.environ.get('RENDER') is not None or os.environ.get('PORT') is not None
    # 2. MUESTREO DE PRODUCCIÓN: Si estamos en Render u otro servidor con 512MB RAM,
    # tomamos solo las 1,000 películas con más votos para mantener el servidor liviano.
    if is_render:
        logging.info("Entorno de Producción detectado (Render): Aplicando catálogo optimizado de 1000 películas.")
        if 'vote_count' in df2.columns:
            df2['vote_count'] = pd.to_numeric(df2['vote_count'], errors='coerce').fillna(0)
            df2 = df2.sort_values('vote_count', ascending=False).head(1000)
        else:
            df2 = df2.head(1000)
    else:
        logging.info("Entorno Local detectado: Procesando el catálogo COMPLETO (4803 películas).")

    df1 = pd.read_csv(Config.CREDITS_PATH, low_memory=False)

    df1['movie_id'] = df1['movie_id'].astype(str)
    df2['id'] = df2['id'].astype(str)

    # Merge de datos ya reducidos
    df = pd.merge(df2, df1, left_on='id', right_on='movie_id')
    del df1, df2
    
    logging.info(f"Merged dataframe shape para producción: {df.shape}")

    if 'title' not in df.columns:
        df['title'] = df['original_title'] if 'original_title' in df.columns else 'Unknown Title'

    df['overview'] = df['overview'].fillna('')
    
    # 3. TF-IDF ultraligero
    tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
    tfidf_matrix = tfidf.fit_transform(df['overview'])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix).astype(np.float32)
    del tfidf_matrix

    features = ['cast', 'crew', 'keywords', 'genres']
    for feature in features:
        if feature in df.columns:
            df[feature] = df[feature].apply(safe_literal_eval)
        else:
            df[feature] = [[] for _ in range(len(df))]

    df['director'] = df['crew'].apply(get_director)
    for feature in ['cast', 'keywords', 'genres']:
        df[feature] = df[feature].apply(get_list)

    for feature in ['cast', 'keywords', 'director', 'genres']:
        df[feature] = df[feature].apply(clean_data)

    df['soup'] = df.apply(create_soup, axis=1)

    # 4. CountVectorizer ultraligero
    count = CountVectorizer(stop_words='english', max_features=1000)
    count_matrix = count.fit_transform(df['soup'])
    cosine_sim2 = cosine_similarity(count_matrix, count_matrix).astype(np.float32)
    del count_matrix

    df = df.reset_index(drop=True)
    indices = pd.Series(df.index, index=df['title']).drop_duplicates()

    logging.info("Procesamiento liviano completado con éxito")
    return df, cosine_sim2, indices

def get_director(x):
    if isinstance(x, list):
        for i in x:
            if isinstance(i, dict) and i.get('job') == 'Director':
                return i.get('name', '')
    return ''

def get_list(x):
    if isinstance(x, list):
        names = [i['name'] for i in x if isinstance(i, dict) and 'name' in i]
        return names[:3] if len(names) > 3 else names
    return []

def clean_data(x):
    if isinstance(x, list):
        return [str.lower(i.replace(" ", "")) for i in x]
    elif isinstance(x, str):
        return str.lower(x.replace(" ", ""))
    else:
        return ''

def create_soup(x):
    keywords = ' '.join(x['keywords']) if isinstance(x['keywords'], list) else ''
    cast = ' '.join(x['cast']) if isinstance(x['cast'], list) else ''
    director = x['director'] if isinstance(x['director'], str) else ''
    genres = ' '.join(x['genres']) if isinstance(x['genres'], list) else ''
    return f"{keywords} {cast} {director} {genres}"

def safe_literal_eval(val):
    try:
        return literal_eval(val)
    except (ValueError, SyntaxError, TypeError):
        return []