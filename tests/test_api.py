from typing import Any

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app


class FakeCollection:
    def __init__(self):
        self._data = []
        self._id = 1

    async def insert_one(self, document):
        document: dict[str, Any] = dict(document)
        document["_id"] = self._id
        self._id += 1
        self._data.append(document)

        class R:
            inserted_id = document["_id"]

        return R()

    async def find_one(self, query):
        _id = query.get("_id")
        for document in self._data:
            if document.get("_id") == _id:
                return document
        return None

    def find(self, query=None, projection=None):

        def gen():
            for document in self._data:
                yield document

        class Cursor:
            def __init__(self, gen):
                self._it = gen()

            def sort(self, *args, **kwargs):
                return self

            def skip(self, n):
                return self

            def limit(self, n):
                return self

            async def __aiter__(self):
                for item in gen():
                    yield item

        return Cursor(gen)

    async def create_index(self, *args, **kwargs):
        return None

    def aggregate(self, pipeline):

        async def gen():
            for document in self._data:
                yield document

        class Cursor:
            def __init__(self, gen):
                self._gen = gen

            async def __aiter__(self):
                async for item in self._gen():
                    yield item

        return Cursor(gen)


def test_post_and_get_document(monkeypatch):
    fake = FakeCollection()

    def fake_get_collection(name):
        return fake

    monkeypatch.setattr("app.main.get_collection", fake_get_collection)

    client = TestClient(app)

    payload = {
        "titulo": "Teste documento",
        "autor": "Autor",
        "conteudo": "Conteúdo sobre carros antigos em Porto Alegre",
        "data": "2025-01-01",
        "latitude": -30.0,
        "longitude": -51.0,
    }

    response = client.post("/documentos", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["titulo"] == payload["titulo"]

    response2 = client.get("/documentos", params={"palavraChave": "carros"})
    assert response2.status_code == status.HTTP_200_OK
    body = response2.json()
    assert body["results"]


def test_get_document_with_palavra_chave(monkeypatch):
    fake = FakeCollection()

    def fake_get_collection(name):
        return fake

    monkeypatch.setattr("app.main.get_collection", fake_get_collection)

    client = TestClient(app)

    payload = {
        "titulo": "Teste documento",
        "autor": "Autor",
        "conteudo": "Conteúdo sobre carros antigos em Porto Alegre",
        "data": "2025-01-01",
        "latitude": -30.0,
        "longitude": -51.0,
    }

    response = client.post("/documentos", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    response2 = client.get("/documentos", params={"palavraChave": "carros"})
    assert response2.status_code == status.HTTP_200_OK
    body = response2.json()
    assert body["results"]


def test_get_document_with_geo(monkeypatch):
    fake = FakeCollection()

    def fake_get_collection(name):
        return fake

    monkeypatch.setattr("app.main.get_collection", fake_get_collection)

    client = TestClient(app)

    payload = {
        "titulo": "Teste documento",
        "autor": "Autor",
        "conteudo": "Conteúdo sobre carros antigos em Porto Alegre",
        "data": "2025-01-01",
        "latitude": -30.0,
        "longitude": -51.0,
    }

    response = client.post("/documentos", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    response2 = client.get(
        "/documentos",
        params={
            "palavraChave": "carros",
            "latitude": -30.0,
            "longitude": -51.0,
        },
    )
    assert response2.status_code == status.HTTP_200_OK
    body = response2.json()
    assert body["results"]


def test_post_document_invalid_lat_lon(monkeypatch):
    """
    Testa a criação de um documento com latitude/longitude inválidas.
    """
    fake = FakeCollection()
    monkeypatch.setattr("app.main.get_collection", lambda name: fake)
    client = TestClient(app)

    payload = {
        "titulo": "Teste",
        "autor": "Autor",
        "conteudo": "Conteúdo",
        "data": "2025-01-01",
        "latitude": "invalid",
        "longitude": "invalid",
    }

    response = client.post("/documentos", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "latitude" in response.text
    assert "longitude" in response.text


def test_post_document_creation_fails(monkeypatch):
    """
    Testa se um erro 500 é retornado quando a criação do documento falha.
    """

    async def mock_create_document(*args, **kwargs):
        return None

    monkeypatch.setattr("app.main.create_document", mock_create_document)
    monkeypatch.setattr(
        "app.main.get_collection", lambda name: FakeCollection()
    )
    client = TestClient(app)

    payload = {
        "titulo": "Teste",
        "autor": "Autor",
        "conteudo": "Conteúdo",
        "data": "2025-01-01",
    }

    response = client.post("/documentos", json=payload)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Could not create document"


def test_get_documents_no_query_param(monkeypatch):
    """
    Testa se um erro 400 é retornado quando nenhum parâmetro de busca é fornecido.
    """
    client = TestClient(app)
    response = client.get("/documentos")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.json()["detail"]
        == "Provide 'palavra_chave' or 'busca' query param"
    )


def test_get_document_with_phrase_search(monkeypatch):
    """
    Testa a busca de um documento usando uma frase com espaços.
    """
    fake = FakeCollection()
    monkeypatch.setattr("app.main.get_collection", lambda name: fake)
    client = TestClient(app)

    payload = {
        "titulo": "Documento de Teste",
        "autor": "Autor",
        "conteudo": "Conteúdo sobre carros antigos em Porto Alegre",
        "data": "2025-01-01",
    }
    client.post("/documentos", json=payload)

    response = client.get("/documentos", params={"busca": "carros antigos"})
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["results"]


def test_build_regex_query_directly():
    """
    Testa a função build_regex_query diretamente.
    """
    from app.crud import build_regex_query

    query = build_regex_query("teste")
    assert "$or" in query
    assert len(query["$or"]) == 3
    assert "titulo" in query["$or"][0]
    assert "conteudo" in query["$or"][1]
    assert "autor" in query["$or"][2]


def test_find_documents_with_skip(monkeypatch):
    """
    Testa a função find_documents com o parâmetro skip.
    """
    fake = FakeCollection()
    monkeypatch.setattr("app.main.get_collection", lambda name: fake)
    client = TestClient(app)

    for i in range(5):
        payload = {
            "titulo": f"Documento {i}",
            "autor": "Autor",
            "conteudo": f"Conteúdo {i}",
            "data": "2025-01-01",
        }
        client.post("/documentos", json=payload)

    response = client.get(
        "/documentos",
        params={"palavraChave": "Documento", "page": 2, "limit": 2},
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["page"] == 2
    assert body["limit"] == 2


def test_search_with_geo_with_skip(monkeypatch):
    """
    Testa a função search_with_geo com o parâmetro skip para cobrir a linha 71.
    """
    fake = FakeCollection()
    monkeypatch.setattr("app.main.get_collection", lambda name: fake)
    client = TestClient(app)

    for i in range(5):
        payload = {
            "titulo": f"Documento {i}",
            "autor": "Autor",
            "conteudo": f"Conteúdo {i}",
            "data": "2025-01-01",
            "latitude": -30.0 + i * 0.1,
            "longitude": -51.0 + i * 0.1,
        }
        client.post("/documentos", json=payload)

    response = client.get(
        "/documentos",
        params={
            "palavraChave": "Documento",
            "latitude": -30.0,
            "longitude": -51.0,
            "page": 2,
            "limit": 2,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["page"] == 2
    assert body["limit"] == 2


def test_post_document_with_valid_coordinates(monkeypatch):
    """
    Testa a criação de um documento com coordenadas válidas.
    """
    fake = FakeCollection()
    monkeypatch.setattr("app.main.get_collection", lambda name: fake)
    client = TestClient(app)

    payload = {
        "titulo": "Teste com coordenadas",
        "autor": "Autor",
        "conteudo": "Conteúdo",
        "data": "2025-01-01",
        "latitude": -30.0334,
        "longitude": -51.2300,
    }

    response = client.post("/documentos", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["latitude"] == -30.0334
    assert data["longitude"] == -51.2300


def test_text_query_build_exception(monkeypatch):
    """
    Testa o tratamento de exceção ao construir a query de texto.
    """
    fake = FakeCollection()
    monkeypatch.setattr("app.main.get_collection", lambda name: fake)

    def mock_build_text_query(*args, **kwargs):
        raise Exception("Query build failed")

    monkeypatch.setattr(
        "app.main.build_text_query_from_phrase", mock_build_text_query
    )
    client = TestClient(app)

    payload = {
        "titulo": "Documento de Teste",
        "autor": "Autor",
        "conteudo": "Conteúdo teste",
        "data": "2025-01-01",
    }
    client.post("/documentos", json=payload)

    response = client.get("/documentos", params={"busca": "teste"})
    assert response.status_code == status.HTTP_200_OK


def test_document_with_direct_lat_lon_fields(monkeypatch):
    """
    Testa documento com campos diretos de latitude/longitude (não GeoJSON).
    """

    class FakeCollectionWithDirectCoords(FakeCollection):
        async def find_one(self, query):
            doc = await super().find_one(query)
            if doc and doc.get("location"):
                doc.pop("location", None)
                doc["latitude"] = -30.0
                doc["longitude"] = -51.0
            return doc

    fake_with_coords = FakeCollectionWithDirectCoords()
    monkeypatch.setattr(
        "app.main.get_collection", lambda name: fake_with_coords
    )
    client = TestClient(app)

    payload = {
        "titulo": "Documento direto",
        "autor": "Autor",
        "conteudo": "Conteúdo",
        "data": "2025-01-01",
        "latitude": -30.0,
        "longitude": -51.0,
    }
    response = client.post("/documentos", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    response = client.get("/documentos", params={"palavraChave": "direto"})
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["results"]


def test_document_with_distance_field(monkeypatch):
    """
    Testa documento com campo distance_m da busca geográfica para cobrir a linha 161.
    """

    class FakeCollectionWithDistance(FakeCollection):
        def aggregate(self, pipeline):
            async def gen():
                for document in self._data:
                    doc_with_distance: dict[str, Any] = dict(document)
                    doc_with_distance["distance_m"] = 1234.56
                    yield doc_with_distance

            class Cursor:
                def __init__(self, gen):
                    self._gen = gen

                async def __aiter__(self):
                    async for item in self._gen():
                        yield item

            return Cursor(gen)

    fake_with_distance = FakeCollectionWithDistance()
    monkeypatch.setattr(
        "app.main.get_collection", lambda name: fake_with_distance
    )
    client = TestClient(app)

    payload = {
        "titulo": "Documento com distância",
        "autor": "Autor",
        "conteudo": "Conteúdo",
        "data": "2025-01-01",
        "latitude": -30.0,
        "longitude": -51.0,
    }
    client.post("/documentos", json=payload)

    response = client.get(
        "/documentos",
        params={
            "palavraChave": "distância",
            "latitude": -30.05,
            "longitude": -51.05,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["results"]

    if body["results"]:
        assert "distance_m" in body["results"][0]
        assert body["results"][0]["distance_m"] == 1234.56


def test_post_document_with_invalid_coordinate_conversion(monkeypatch):
    """
    Testa o tratamento de exceção quando a conversão de coordenadas para float falha.
    """
    fake = FakeCollection()
    monkeypatch.setattr("app.main.get_collection", lambda name: fake)

    client = TestClient(app)

    payload = {
        "titulo": "Teste",
        "autor": "Autor",
        "conteudo": "Conteúdo",
        "data": "2025-01-01",
        "latitude": "aa",
        "longitude": "bb",
    }

    response = client.post("/documentos", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_get_documents_query_exception(monkeypatch):
    """
    Testa o tratamento de exceção durante a busca de documentos.
    """
    fake = FakeCollection()

    async def mock_find_documents(*args, **kwargs):
        raise Exception("Database error")

    monkeypatch.setattr("app.main.get_collection", lambda name: fake)
    monkeypatch.setattr("app.main.find_documents", mock_find_documents)
    monkeypatch.setattr(
        "app.main.build_text_query_from_phrase", lambda x: None
    )

    client = TestClient(app)

    payload = {
        "titulo": "Documento de Teste",
        "autor": "Autor",
        "conteudo": "Conteúdo teste",
        "data": "2025-01-01",
    }
    client.post("/documentos", json=payload)

    response = client.get("/documentos", params={"palavraChave": "teste"})
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Error querying documents"
