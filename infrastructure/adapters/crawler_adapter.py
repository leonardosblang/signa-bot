import asyncio
from typing import List, Dict, Any, Optional
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from ports.crawler_port import CrawlerPort
from infrastructure.config import config
from bs4 import BeautifulSoup
import re
from tenacity import retry, stop_after_attempt, wait_exponential

class SignaCrawlerAdapter(CrawlerPort):
    def __init__(self):
        self.base_url = "https://www.signa.pt"
        self.browser_config = BrowserConfig(
            headless=True
        )
        
    async def crawl_site(self, base_url: str) -> Dict[str, Any]:
        config.log_debug(f"Starting site crawl for {base_url}")
        
        categories = await self._crawl_categories()
        products = []
        
        for category in categories[:5] if config.debug_mode else categories:
            config.log_debug(f"Crawling category: {category['name']}")
            category_products = await self._crawl_category(category)
            products.extend(category_products)
            
        return {
            "categories": categories,
            "products": products,
            "base_url": base_url
        }
    
    @retry(stop=stop_after_attempt(config.max_retries), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def crawl_page(self, url: str) -> str:
        config.log_debug(f"Crawling page: {url}")
        
        async with AsyncWebCrawler(browser_config=self.browser_config) as crawler:
            result = await crawler.arun(
                url=url,
                config=CrawlerRunConfig(
                    cache_mode=CacheMode.ENABLED if config.cache_enabled else CacheMode.DISABLED,
                    wait_for_network_idle=True
                )
            )
            return result.html
    
    async def extract_products(self, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, 'lxml')
        products = []
        
        for product_div in soup.find_all('div', class_='product-item'):
            product = self._parse_product(product_div)
            if product:
                products.append(product)
                
        return products
    
    async def extract_categories(self, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, 'lxml')
        categories = []
        
        menu = soup.find('nav', class_='main-menu') or soup.find('ul', class_='menu-categories')
        if not menu:
            return categories
            
        for category_li in menu.find_all('li', recursive=False):
            category = self._parse_category(category_li)
            if category:
                categories.append(category)
                
        return categories
    
    async def _crawl_categories(self) -> List[Dict[str, Any]]:
        html = await self.crawl_page(self.base_url)
        return await self.extract_categories(html)
    
    async def _crawl_category(self, category: Dict[str, Any]) -> List[Dict[str, Any]]:
        products = []
        category_url = f"{self.base_url}{category['url']}" if not category['url'].startswith('http') else category['url']
        
        html = await self.crawl_page(category_url)
        category_products = await self.extract_products(html)
        
        for product in category_products:
            product['category'] = category['name']
            product['category_id'] = category.get('id')
            products.append(product)
            
        return products
    
    def _parse_product(self, product_div) -> Optional[Dict[str, Any]]:
        try:
            name_elem = product_div.find('h3') or product_div.find('a', class_='product-name')
            if not name_elem:
                return None
                
            product_data = {
                'name': name_elem.get_text(strip=True),
                'url': '',
                'price': None,
                'colors': [],
                'id': ''
            }
            
            link = product_div.find('a', href=True)
            if link:
                product_data['url'] = link['href']
                if not product_data['url'].startswith('http'):
                    product_data['url'] = f"{self.base_url}{product_data['url']}"
                    
                id_match = re.search(r'id=(\d+)', product_data['url'])
                if id_match:
                    product_data['id'] = id_match.group(1)
            
            price_elem = product_div.find('span', class_='price') or product_div.find('div', class_='price')
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'(\d+[.,]\d+)', price_text)
                if price_match:
                    product_data['price'] = float(price_match.group(1).replace(',', '.'))
            
            color_elems = product_div.find_all('span', class_='color') or product_div.find_all('div', class_='color-option')
            product_data['colors'] = [color.get('title', color.get_text(strip=True)) for color in color_elems]
            
            return product_data
            
        except Exception as e:
            config.log_debug(f"Error parsing product: {e}")
            return None
    
    def _parse_category(self, category_li) -> Optional[Dict[str, Any]]:
        try:
            link = category_li.find('a', href=True)
            if not link:
                return None
                
            category_data = {
                'name': link.get_text(strip=True),
                'url': link['href'],
                'subcategories': []
            }
            
            id_match = re.search(r'idCategoria=(\d+)', link['href'])
            if id_match:
                category_data['id'] = int(id_match.group(1))
            
            submenu = category_li.find('ul', class_='submenu') or category_li.find('div', class_='dropdown-menu')
            if submenu:
                for sub_li in submenu.find_all('li'):
                    sub_link = sub_li.find('a', href=True)
                    if sub_link:
                        subcategory = {
                            'name': sub_link.get_text(strip=True),
                            'url': sub_link['href']
                        }
                        
                        sub_id_match = re.search(r'idSubCategoria=(\d+)', sub_link['href'])
                        if sub_id_match:
                            subcategory['id'] = int(sub_id_match.group(1))
                            
                        category_data['subcategories'].append(subcategory)
            
            return category_data
            
        except Exception as e:
            config.log_debug(f"Error parsing category: {e}")
            return None