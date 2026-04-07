"""Topic modeling sobre abstracts: LDA y BERTopic."""

import pandas as pd
from loguru import logger


def fit_lda(
    df: pd.DataFrame,
    column: str = "Abstract",
    n_topics: int = 8,
    max_features: int = 1000,
    random_state: int = 42,
) -> tuple[pd.DataFrame, list[list[str]]]:
    """Ajusta LDA sobre los abstracts y asigna topic dominante a cada artículo.

    Args:
        df: DataFrame WoS.
        column: Columna con texto de abstracts.
        n_topics: Número de topics a detectar.
        max_features: Vocabulario máximo para TF-IDF.
        random_state: Semilla.

    Returns:
        Tupla (df_con_topics, topic_words) donde:
        - df_con_topics tiene columna 'lda_topic' con el topic dominante.
        - topic_words es lista de listas con las top 10 palabras por topic.
    """
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.feature_extraction.text import TfidfVectorizer

    abstracts = df[column].dropna()
    logger.info("LDA: procesando {} abstracts con {} topics...", len(abstracts), n_topics)

    vectorizer = TfidfVectorizer(max_features=max_features, stop_words="english")
    X = vectorizer.fit_transform(abstracts)

    lda = LatentDirichletAllocation(n_components=n_topics, random_state=random_state)
    lda.fit(X)

    # Asignar topic dominante
    topic_assignments = lda.transform(X).argmax(axis=1)
    df = df.copy()
    df.loc[abstracts.index, "lda_topic"] = topic_assignments

    # Extraer palabras top por topic
    feature_names = vectorizer.get_feature_names_out()
    topic_words = []
    for topic_idx, topic in enumerate(lda.components_):
        top_words = [feature_names[i] for i in topic.argsort()[:-11:-1]]
        topic_words.append(top_words)
        logger.info("Topic {}: {}", topic_idx, ", ".join(top_words))

    return df, topic_words


def fit_bertopic(
    df: pd.DataFrame,
    column: str = "Abstract",
    nr_topics: int = 10,
    language: str = "english",
) -> tuple[pd.DataFrame, object]:
    """Ajusta BERTopic sobre los abstracts.

    Más sofisticado que LDA, mejor para corpus pequeños (~331 docs).

    Args:
        df: DataFrame WoS.
        column: Columna con texto de abstracts.
        nr_topics: Número de topics objetivo.
        language: Idioma de los documentos.

    Returns:
        Tupla (df_con_topics, topic_model) donde:
        - df_con_topics tiene columna 'bertopic' con el topic asignado.
        - topic_model es el modelo BERTopic ajustado.
    """
    from bertopic import BERTopic

    abstracts = df[column].dropna().tolist()
    abstract_idx = df[column].dropna().index

    logger.info("BERTopic: procesando {} abstracts...", len(abstracts))
    topic_model = BERTopic(language=language, nr_topics=nr_topics)
    topics, _probs = topic_model.fit_transform(abstracts)

    df = df.copy()
    df.loc[abstract_idx, "bertopic"] = topics

    topic_info = topic_model.get_topic_info()
    logger.info("BERTopic: {} topics detectados", len(topic_info) - 1)  # -1 por outlier topic

    return df, topic_model
