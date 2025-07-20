from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class CrawlerPort(ABC):
    @abstractmethod
    async def crawl_site(self, base_url: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def crawl_page(self, url: str) -> str:
        pass
    
    @abstractmethod
    async def extract_products(self, html: str) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def extract_categories(self, html: str) -> List[Dict[str, Any]]:
        pass