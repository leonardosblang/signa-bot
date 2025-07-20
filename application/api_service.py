from typing import Optional, Dict, Any
from application.chatbot_service import ChatbotService
from application.crawler_service import CrawlerService
from ports.chatbot_port import ChatbotPort
from ports.knowledge_base_port import KnowledgeBasePort
from ports.crawler_port import CrawlerPort
from domain.models import SearchQuery, SearchResult
from infrastructure.config import config
import asyncio


class SignaChatbotService:
    def __init__(self, chatbot: ChatbotPort, knowledge_base: KnowledgeBasePort, crawler: CrawlerPort):
        self.chatbot_service = ChatbotService(chatbot, knowledge_base)
        self.crawler_service = CrawlerService(crawler, knowledge_base)
        self.knowledge_base = knowledge_base
        self.chatbot = chatbot
        self._initialized = False
        
    async def initialize(self):
        if self._initialized:
            return
            
        data = await self.knowledge_base.get_all_data()
        if data['total_products'] == 0:
            config.log_debug("Base de conhecimento vazia. Iniciando crawling...")
            try:
                await self.crawler_service.crawl_and_index()
            except Exception as e:
                config.log_debug(f"Erro durante crawling: {e}")
        
        self._initialized = True
    
    async def process_query_text(self, query_text: str):
        await self.initialize()
        
        response_text = await self.chatbot_service.chat(query_text)
        
        # Try to extract products and links from the response  
        products = []
        search_link = None
        
        if hasattr(self.chatbot, 'search_products'):
            try:
                # Use the chatbot's own analysis method
                if hasattr(self.chatbot, '_analyze_and_correct_query'):
                    query_info = await self.chatbot._analyze_and_correct_query(query_text)
                    
                    if query_info.get('type') == 'product_search':
                        search_query = SearchQuery(
                            text=query_info.get('product'),
                            category=query_info.get('category'),
                            color=query_info.get('color'),
                            price_min=query_info.get('price_min'),
                            price_max=query_info.get('price_max')
                        )
                        
                        search_result = await self.chatbot.search_products(search_query)
                        products = search_result.products or []
                        search_link = search_result.filter_url
                        
            except Exception as e:
                config.log_debug(f"Erro na pesquisa de produtos: {e}")
        
        # Create a simple response object that works with both API formats
        class SimpleResponse:
            def __init__(self, text, products=None, metadata=None):
                self.text = text
                self.products = products or []
                self.metadata = metadata or {}
                if search_link:
                    self.metadata['search_link'] = search_link
        
        return SimpleResponse(response_text, products, {'search_link': search_link} if search_link else {})
    
    async def get_stats(self) -> Dict[str, Any]:
        return await self.chatbot_service.get_stats()
    
    def clear_history(self):
        self.chatbot_service.clear_history()
    
    async def crawl_site(self):
        return await self.crawler_service.crawl_and_index()