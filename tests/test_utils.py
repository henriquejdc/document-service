from app.utils import haversine_distance, normalize_search_phrase


def test_haversine_zero():
    d = haversine_distance(0, 0, 0, 0)
    assert d == 0


def test_haversine_known():
    # distance between two nearby points should be > 0
    d = haversine_distance(-30.0, -51.0, -30.001, -51.001)
    assert d > 0


def test_normalize():
    assert normalize_search_phrase("  hello world  ") == "hello world"
