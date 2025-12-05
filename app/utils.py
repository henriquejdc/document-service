import math


def haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calcula a distância em metros entre dois pontos geográficos
    (latitude/longitude) usando a fórmula de Haversine.
    """
    r = 6371000.0  # Raio da Terra em metros

    # Converte as latitudes de graus para radianos
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    # Calcula a diferença de latitude e longitude em radianos
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    # Aplica a fórmula de Haversine: calcula o quadrado da metade da corda entre os pontos
    a = (
        math.sin(d_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2.0) ** 2
    )

    # Calcula a distância angular em radianos
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Retorna a distância final multiplicando a distância angular pelo raio da Terra
    return r * c


def normalize_search_phrase(phrase: str) -> str:
    """
    Normaliza uma frase de busca removendo espaços em branco
    no início e no fim.
    """
    return phrase.strip()
