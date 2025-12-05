import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import RedirectResponse

from .crud import (
    build_regex_query,
    build_text_query_from_phrase,
    create_document,
    find_documents,
    search_with_geo,
)
from .db import connect, get_collection, get_db_name
from .schemas import DocumentCreate, DocumentOut

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover
    mongo = await connect()
    db = mongo[get_db_name()]
    coll = db["documents"]

    try:
        await coll.create_index(
            [("titulo", "text"), ("conteudo", "text"), ("autor", "text")],
            name="text_idx",
        )
    except Exception as e:
        logger.exception("Could not create text index: %s", str(e))
    try:
        await coll.create_index(
            [("location", "2dsphere")], name="location_2dsphere"
        )

    except Exception as e:
        logger.exception("Could not create 2dsphere index: %s", str(e))

    logger.info("Connected to MongoDB and ensured indexes")
    yield


app = FastAPI(
    title="Document Service API",
    description="""
    ## API de Gerenciamento de Documentos

    Esta API permite criar e buscar documentos com suporte a:
    
    * **Busca por texto**: Busca em títulos, conteúdo e autores
    * **Busca por frase**: Busca por frases exatas
    * **Busca geográfica**: Busca documentos próximos a coordenadas específicas
    * **Paginação**: Controle de page e limit para resultados
    
    ### Endpoints Disponíveis
    
    * `POST /documentos` - Cria um novo documento
    * `GET /documentos` - Busca documentos com diversos filtros
    """,
    version="1.0.0",
    contact={
        "name": "Henrique J. D. Corte",
        "email": "riquejdc@gmail.com",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "documentos",
            "description": "Operações relacionadas a documentos: criação e busca.",
        }
    ],
)


@app.get("/", include_in_schema=False)
async def root(): # pragma: no cover
    """Redireciona a URL raiz para a documentação Swagger."""
    return RedirectResponse(url="/docs")


@app.post(
    "/documentos",
    response_model=DocumentOut,
    tags=["documentos"],
    status_code=status.HTTP_201_CREATED,
    summary="Criar um novo documento",
    description="""
    Cria um novo documento no sistema.
    
    Se latitude e longitude forem fornecidas, o documento será indexado geograficamente,
    permitindo buscas por proximidade.
    """,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Documento criado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "_id": "507f1f77bcf86cd799439011",
                        "titulo": "História de Porto Alegre",
                        "autor": "João Silva",
                        "conteudo": "Porto Alegre é a capital do Rio Grande do Sul...",
                        "data": "2025-01-15",
                        "latitude": -30.0346,
                        "longitude": -51.2177,
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {"description": "Coordenadas inválidas"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Erro ao criar documento"
        },
    },
)
async def post_document(document: DocumentCreate):
    collection = get_collection("documents")
    data = document.model_dump()

    if data.get("latitude") is not None and data.get("longitude") is not None:
        latitude_val = data.get("latitude")
        longitude_val = data.get("longitude")
        data["location"] = {
            "type": "Point",
            "coordinates": [longitude_val, latitude_val],
        }

    created = await create_document(collection, data)
    if not created:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create document",
        )

    created["_id"] = str(created.get("_id"))
    return created


@app.get(
    "/documentos",
    tags=["documentos"],
    summary="Buscar documentos",
    description="""
    Busca documentos no sistema usando diversos critérios.
    
    ## Parâmetros de Busca
    
    * **palavraChave**: Busca por palavra-chave em título, conteúdo e autor (regex)
    * **busca**: Busca por frase usando indexação de texto (mais preciso para frases)
    * **latitude/longitude**: Coordenadas para busca geográfica (retorna documentos próximos)
    * **page**: Número da página (padrão: 1)
    * **limit**: Número de resultados por página (padrão: 20, máximo: 200)
    
    ## Exemplos de Uso
    
    * Busca simples: `?palavraChave=historia`
    * Busca por frase: `?busca=Porto Alegre`
    * Busca geográfica: `?palavraChave=museu&latitude=-30.0346&longitude=-51.2177`
    * Com paginação: `?palavraChave=arte&page=2&limit=10`
    
    **Nota**: Pelo menos um dos parâmetros `palavraChave` ou `busca` deve ser fornecido.
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Busca realizada com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "page": 1,
                        "limit": 20,
                        "results": [
                            {
                                "_id": "507f1f77bcf86cd799439011",
                                "titulo": "História de Porto Alegre",
                                "autor": "João Silva",
                                "conteudo": "Porto Alegre é a capital...",
                                "data": "2025-01-15",
                                "latitude": -30.0346,
                                "longitude": -51.2177,
                                "distance_m": 1234.56,
                            }
                        ],
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Parâmetros de busca ausentes ou inválidos"
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Erro ao buscar documentos"
        },
    },
)
async def get_documents(
    palavra_chave: Optional[str] = Query(None, alias="palavraChave"),
    busca: Optional[str] = Query(None),
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
):
    if not palavra_chave and not busca:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide 'palavra_chave' or 'busca' query param",
        )

    collection = get_collection("documents")

    text_query = None
    use_text = False
    try:
        if busca:
            text_query = build_text_query_from_phrase(busca)
            use_text = True

        elif palavra_chave:
            text_query = build_text_query_from_phrase(palavra_chave)
            use_text = True

    except Exception as e:
        logger.exception(
            "Text query build failed; falling back to regex: error=%s", str(e)
        )

    skip = (page - 1) * limit

    try:
        if latitude is not None and longitude is not None:
            documents = await search_with_geo(
                collection,
                text_query,
                latitude,
                longitude,
                limit=limit,
                skip=skip,
            )
        else:
            if use_text and text_query is not None:
                cursor = (
                    collection.find(
                        text_query, {"score": {"$meta": "textScore"}}
                    )
                    .sort([("score", {"$meta": "textScore"})])
                    .skip(skip)
                    .limit(limit)
                )
                documents = [d async for d in cursor]

            else:
                query_filter = build_regex_query(
                    palavra_chave if palavra_chave else busca
                )
                documents = await find_documents(
                    collection, query_filter, limit=limit, skip=skip
                )

    except Exception:
        logger.exception("Error querying documents")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error querying documents",
        )

    results = []
    for document in documents:
        document_out = {
            "_id": str(document.get("_id")) if document.get("_id") else None,
            "titulo": document.get("titulo"),
            "autor": document.get("autor"),
            "conteudo": document.get("conteudo"),
            "data": document.get("data"),
            "latitude": None,
            "longitude": None,
        }

        if document.get("location") and isinstance(
            document.get("location"), dict
        ):
            coords = document.get("location").get("coordinates")
            if coords and len(coords) >= 2:
                document_out["longitude"] = coords[0]
                document_out["latitude"] = coords[1]
        else:
            document_out["latitude"] = document.get("latitude")
            document_out["longitude"] = document.get("longitude")

        if document.get("distance_m") is not None:
            document_out["distance_m"] = document.get("distance_m")

        results.append(document_out)

    return {"page": page, "limit": limit, "results": results}
