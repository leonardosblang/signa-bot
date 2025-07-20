from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Pergunta do utilizador")
    session_id: Optional[str] = Field(None, description="ID da sessão para manter contexto")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="Resposta gerada pelo chatbot")
    products: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Produtos encontrados")
    search_link: Optional[str] = Field(None, description="Link de pesquisa filtrada")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confiança na resposta")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados adicionais")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Estado do serviço")
    timestamp: datetime = Field(..., description="Timestamp atual")
    version: str = Field(default="1.0.0", description="Versão da API")
    products_count: int = Field(default=0, description="Número de produtos na base")
    categories_count: int = Field(default=0, description="Número de categorias")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Mensagem de erro")
    detail: Optional[str] = Field(None, description="Detalhes adicionais")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp do erro")