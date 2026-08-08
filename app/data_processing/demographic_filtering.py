import pandas as pd
import numpy as np
from config.config import Config

def load_and_process_data():
    # 1. Leer solo las columnas estrictamente necesarias de cada CSV
    cols_credits = ['movie_id', 'cast', 'crew']
    cols_metadata = ['id', 'original_title', 'title', 'vote_count', 'vote_average']

    df1 = pd.read_csv(Config.CREDITS_PATH, usecols=lambda c: c in cols_credits, low_memory=False)
    df2 = pd.read_csv(Config.MOVIES_METADATA_PATH, usecols=lambda c: c in cols_metadata, low_memory=False)

    df1['movie_id'] = df1['movie_id'].astype(str)
    df2['id'] = df2['id'].astype(str)

    # 2. Realizar el merge
    df = pd.merge(df2, df1, left_on='id', right_on='movie_id', how='inner')
    del df1, df2  # Liberar memoria de los DataFrames principales
    
    title_col = 'original_title' if 'original_title' in df.columns else 'title'
    df = df[['id', title_col, 'vote_count', 'vote_average']].copy()
    if title_col != 'title':
        df = df.rename(columns={title_col: 'title'})

    # Convertir métricas a numérico y optimizar tipos
    df['vote_count'] = pd.to_numeric(df['vote_count'], errors='coerce').fillna(0).astype('int32')
    df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce').fillna(0).astype('float32')

    C = df['vote_average'].mean()
    m = df['vote_count'].quantile(0.9)

    # 3. Filtrar directamente sin duplicar el objeto completo
    q_movies = df[df['vote_count'] >= m].copy()
    del df  # Liberar el DataFrame original

    # Calcular score vectorizado (mucho más rápido y eficiente en RAM que .apply)
    v = q_movies['vote_count'].values
    R = q_movies['vote_average'].values
    q_movies['score'] = (v / (v + m) * R) + (m / (m + v) * C)

    q_movies = q_movies.sort_values('score', ascending=False)

    return q_movies[['id', 'title', 'vote_count', 'vote_average', 'score']]

def get_top_movies(n=10):
    qualified_movies = load_and_process_data()
    return qualified_movies.head(n)