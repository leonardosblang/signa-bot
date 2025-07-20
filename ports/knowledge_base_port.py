from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class KnowledgeBasePort(ABC):
    @abstractmethod
    async def store_products(self, products: List[Dict[str, Any]]) -> None:
        pass
    
    @abstractmethod
    async def store_categories(self, categories: List[Dict[str, Any]]) -> None:
        pass
    
    @abstractmethod
    async def search_products(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def get_category_info(self, category_name: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def get_all_data(self) -> Dict[str, Any]:
        pass