from typing import Dict, Any
from ports.crawler_port import CrawlerPort
from ports.knowledge_base_port import KnowledgeBasePort
from infrastructure.config import config
import asyncio

class CrawlerService:
    def __init__(self, crawler: CrawlerPort, knowledge_base: KnowledgeBasePort):
        self.crawler = crawler
        self.knowledge_base = knowledge_base
        
    async def crawl_and_index(self, base_url: str = "https://www.signa.pt") -> Dict[str, Any]:
        config.log_debug("Starting crawl and index process")
        
        crawl_result = await self.crawler.crawl_site(base_url)
        
        await self.knowledge_base.store_categories(crawl_result['categories'])
        await self.knowledge_base.store_products(crawl_result['products'])
        
        stats = {
            'categories_crawled': len(crawl_result['categories']),
            'products_crawled': len(crawl_result['products']),
            'base_url': base_url
        }
        
        config.log_debug(f"Crawl completed: {stats}")
        return stats
    
    async def update_category(self, category_name: str) -> Dict[str, Any]:
        config.log_debug(f"Updating category: {category_name}")
        
        category_info = await self.knowledge_base.get_category_info(category_name)
        if not category_info:
            return {'error': f'Category {category_name} not found'}
            
        category_url = f"https://www.signa.pt{category_info['url']}"
        html = await self.crawler.crawl_page(category_url)
        products = await self.crawler.extract_products(html)
        
        for product in products:
            product['category'] = category_info['name']
            product['category_id'] = category_info.get('id')
            
        await self.knowledge_base.store_products(products)
        
        return {
            'category': category_name,
            'products_updated': len(products)
        }