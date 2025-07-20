from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models import ChatMessage, SearchResult, SearchQuery

class ChatbotPort(ABC):
    @abstractmethod
    async def process_message(self, message: str, context: Optional[List[ChatMessage]] = None) -> str:
        pass
    
    @abstractmethod
    async def search_products(self, query: SearchQuery) -> SearchResult:
        pass
    
    @abstractmethod
    async def get_product_by_id(self, product_id: str) -> Optional[dict]:
        pass