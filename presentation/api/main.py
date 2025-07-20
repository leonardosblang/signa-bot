from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from presentation.api.models import (
    ChatRequest, ChatResponse, HealthResponse, ErrorResponse
)
from application.api_service import SignaChatbotService
from infrastructure.adapters.intelligent_chatbot_adapter import IntelligentChatbotAdapter
from infrastructure.adapters.knowledge_base_adapter import InMemoryKnowledgeBase
from infrastructure.adapters.comprehensive_crawler import ComprehensiveCrawlerAdapter
from infrastructure.config import config
from domain.models import SearchQuery, SearchResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicação...")
    
    knowledge_base = InMemoryKnowledgeBase()
    crawler = ComprehensiveCrawlerAdapter()
    chatbot_adapter = IntelligentChatbotAdapter(knowledge_base)
    
    app.state.chatbot_service = SignaChatbotService(chatbot_adapter, knowledge_base, crawler)
    await app.state.chatbot_service.initialize()
    
    yield
    logger.info("Encerrando aplicação...")


app = FastAPI(
    title="Signa Chatbot API",
    description="API para interagir com o chatbot inteligente da Signa",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest):
    try:
        logger.info(f"Nova query recebida: {request.query[:50]}...")
        
        response = await app.state.chatbot_service.process_query_text(request.query)
        
        products_data = []
        if hasattr(response, 'products') and response.products:
            products_data = [
                {
                    "name": product.get('name', ''),
                    "price": product.get('price', 0),
                    "url": product.get('url', ''),
                    "colors": product.get('colors', [])
                }
                for product in response.products[:5]
            ]
        
        search_link = None
        if hasattr(response, 'metadata') and response.metadata:
            search_link = response.metadata.get('search_link')
        
        return ChatResponse(
            answer=response.text,
            products=products_data,
            search_link=search_link,
            confidence=1.0,
            metadata=getattr(response, 'metadata', {})
        )
        
    except Exception as e:
        logger.error(f"Erro ao processar query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar a pergunta: {str(e)}"
        )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    try:
        data = await app.state.chatbot_service.knowledge_base.get_all_data()
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            version="1.0.0",
            products_count=data.get('total_products', 0),
            categories_count=data.get('total_categories', 0)
        )
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            version="1.0.0",
            products_count=0,
            categories_count=0
        )


@app.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def clear_session(session_id: str):
    app.state.chatbot_service.clear_history()
    logger.info(f"Sessão {session_id} limpa")
    return


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Erro não tratado: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Erro interno do servidor",
            "detail": str(exc) if config.debug_mode else None,
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "presentation.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )