from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    """Schema para criação de um novo documento."""

    titulo: str = Field(
        ...,
        description="Título do documento",
        examples=["História de Porto Alegre"],
    )
    autor: str = Field(
        ..., description="Nome do autor do documento", examples=["João Silva"]
    )
    conteudo: str = Field(
        ...,
        description="Conteúdo completo do documento",
        examples=[
            "Porto Alegre é a capital do Rio Grande do Sul, localizada no sul do Brasil..."
        ],
    )
    data: str = Field(
        ...,
        description="Data do documento no formato YYYY-MM-DD",
        examples=["2025-01-15"],
    )
    latitude: Optional[float] = Field(
        None,
        description="Latitude da localização do documento (opcional)",
        examples=[-30.0346],
        ge=-90,
        le=90,
    )
    longitude: Optional[float] = Field(
        None,
        description="Longitude da localização do documento (opcional)",
        examples=[-51.2177],
        ge=-180,
        le=180,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "titulo": "História de Porto Alegre",
                    "autor": "João Silva",
                    "conteudo": "Porto Alegre é a capital do Rio Grande do Sul, localizada no sul do Brasil. Fundada em 1772, a cidade tem uma rica história cultural e arquitetônica.",
                    "data": "2025-01-15",
                    "latitude": -30.0346,
                    "longitude": -51.2177,
                }
            ]
        }
    )


class DocumentOut(BaseModel):
    """Schema para resposta de um documento."""

    id: Optional[str] = Field(
        default=None,
        alias="_id",
        description="ID único do documento (MongoDB ObjectId)",
    )
    titulo: str = Field(..., description="Título do documento")
    autor: str = Field(..., description="Nome do autor do documento")
    conteudo: str = Field(..., description="Conteúdo completo do documento")
    data: str = Field(..., description="Data do documento")
    latitude: Optional[float] = Field(
        None, description="Latitude da localização do documento"
    )
    longitude: Optional[float] = Field(
        None, description="Longitude da localização do documento"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "_id": "507f1f77bcf86cd799439011",
                    "titulo": "História de Porto Alegre",
                    "autor": "João Silva",
                    "conteudo": "Porto Alegre é a capital do Rio Grande do Sul...",
                    "data": "2025-01-15",
                    "latitude": -30.0346,
                    "longitude": -51.2177,
                }
            ]
        },
    )
