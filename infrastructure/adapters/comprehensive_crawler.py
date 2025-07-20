import asyncio
from typing import List, Dict, Any, Optional
from ports.crawler_port import CrawlerPort
from infrastructure.config import config
from bs4 import BeautifulSoup
import aiohttp
import re
import json
from urllib.parse import urlencode, urlparse, parse_qs

class ComprehensiveCrawlerAdapter(CrawlerPort):
    def __init__(self):
        self.base_url = "https://www.signa.pt"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # COMPREHENSIVE color map with ALL colors from Signa
        self.color_map = {
            # Primary colors
            'azul': '117',
            'azuis': '117',
            'blue': '117',
            'vermelho': '130',
            'vermelha': '130',
            'vermelhos': '130',
            'vermelhas': '130',
            'red': '130',
            'verde': '126',
            'verdes': '126',
            'green': '126',
            'preto': '119',
            'preta': '119',
            'pretos': '119',
            'pretas': '119',
            'black': '119',
            'branco': '118',
            'branca': '118',
            'brancos': '118',
            'brancas': '118',
            'white': '118',
            'amarelo': '116',
            'amarela': '116',
            'amarelos': '116',
            'amarelas': '116',
            'yellow': '116',
            'laranja': '125',
            'laranjas': '125',
            'orange': '125',
            'rosa': '128',
            'rosas': '128',
            'pink': '128',
            'cinzento': '120',
            'cinza': '120',
            'cinzentos': '120',
            'cinzas': '120',
            'grey': '120',
            'gray': '120',
            'castanho': '119',
            'castanha': '119',
            'marrom': '119',
            'brown': '119',
            'roxo': '129',
            'roxa': '129',
            'roxos': '129',
            'roxas': '129',
            'purple': '129',
            'violeta': '129',
            'dourado': '121',
            'dourada': '121',
            'dourados': '121',
            'douradas': '121',
            'gold': '121',
            'prateado': '127',
            'prateada': '127',
            'prateados': '127',
            'prateadas': '127',
            'prata': '127',
            'silver': '127',
            'bege': '118',
            'beges': '118',
            'natural': '124',
            'naturais': '124',
            'turquesa': '131',
            'turquoise': '131',
            'bordeaux': '132',
            'bordô': '132',
            'navy': '133',
            'azul-marinho': '133',
            'azul marinho': '133'
        }
        
        # CORRECT category structure from Signa website
        self.categories_structure = {
            44: {"name": "Beleza & Saúde", "subcategories": []},
            32: {"name": "Bricolage & Auto", "subcategories": []},
            30: {"name": "Casa & Lar", "subcategories": [
                {"id": 164, "name": "Canecas Personalizadas"},
                {"id": 165, "name": "Copos"},
                {"id": 166, "name": "Garrafas"},
                {"id": 167, "name": "Termos"}
            ]},
            34: {"name": "Doces", "subcategories": []},
            35: {"name": "Escrita & Escritório", "subcategories": [
                {"id": 170, "name": "Canetas"},
                {"id": 171, "name": "Lápis"},
                {"id": 172, "name": "Marcadores"},
                {"id": 173, "name": "Cadernos"},
                {"id": 174, "name": "Blocos de Notas"}
            ]},
            33: {"name": "Identificadores", "subcategories": [
                {"id": 175, "name": "Porta-Chaves"},
                {"id": 176, "name": "Lanyards"},
                {"id": 177, "name": "Pins"}
            ]},
            39: {"name": "Lazer", "subcategories": []},
            38: {"name": "Pessoais", "subcategories": []},
            37: {"name": "Sacos & Mochilas", "subcategories": [
                {"id": 159, "name": "Mochilas"},
                {"id": 141, "name": "Bolsas"},
                {"id": 180, "name": "Sacos de Compras"},
                {"id": 181, "name": "Sacos de Desporto"}
            ]},
            40: {"name": "Suportes Publicitários", "subcategories": []},
            41: {"name": "Tecnologia", "subcategories": [
                {"id": 190, "name": "PowerBanks"},
                {"id": 191, "name": "Pen Drives"},
                {"id": 192, "name": "Auriculares"},
                {"id": 193, "name": "Colunas"}
            ]},
            31: {"name": "Vestuário", "subcategories": [
                {"id": 200, "name": "T-Shirts"},
                {"id": 201, "name": "Polos"},
                {"id": 202, "name": "Camisas"},
                {"id": 203, "name": "Sweatshirts"},
                {"id": 204, "name": "Casacos"},
                {"id": 205, "name": "Bonés"},
                {"id": 206, "name": "Chapéus"}
            ]}
        }
        
    async def crawl_site(self, base_url: str) -> Dict[str, Any]:
        config.log_debug(f"Starting comprehensive crawl for {base_url}")
        
        # Build categories list from structure
        categories = []
        for cat_id, cat_info in self.categories_structure.items():
            category = {
                "id": cat_id,
                "name": cat_info["name"],
                "url": f"/brindes/categoria.asp?idCategoria={cat_id}",
                "subcategories": cat_info["subcategories"]
            }
            categories.append(category)
        
        # Crawl products from ALL categories
        all_products = []
        total_limit = 500  # Limit total products to avoid timeout
        
        for category in categories:
            if len(all_products) >= total_limit:
                break
                
            if category.get('subcategories'):
                # Crawl each subcategory
                for subcat in category['subcategories']:
                    if len(all_products) >= total_limit:
                        break
                        
                    url = f"{self.base_url}/brindes/categoria.asp?idCategoria={category['id']}&idSubCategoria={subcat['id']}"
                    config.log_debug(f"Crawling: {category['name']} - {subcat['name']}")
                    
                    products = await self._crawl_category_page(url)
                    for product in products[:30]:  # 30 products per subcategory
                        product['category'] = category['name']
                        product['category_id'] = category['id']
                        product['subcategory'] = subcat['name']
                        product['subcategory_id'] = subcat['id']
                        all_products.append(product)
                        
                    config.log_debug(f"Added {len(products[:30])} products from {subcat['name']}")
            else:
                # Crawl main category
                url = f"{self.base_url}/brindes/categoria.asp?idCategoria={category['id']}"
                config.log_debug(f"Crawling: {category['name']}")
                
                products = await self._crawl_category_page(url)
                for product in products[:50]:  # 50 products per main category
                    product['category'] = category['name']
                    product['category_id'] = category['id']
                    all_products.append(product)
                    
                config.log_debug(f"Added {len(products[:50])} products from {category['name']}")
        
        config.log_debug(f"Total products crawled: {len(all_products)}")
        
        return {
            "categories": categories,
            "products": all_products,
            "base_url": base_url,
            "color_map": self.color_map
        }
    
    async def _crawl_category_page(self, url: str) -> List[Dict[str, Any]]:
        """Crawl a single category page and extract products"""
        html = await self.crawl_page(url)
        if html:
            return await self.extract_products(html)
        return []
    
    async def crawl_page(self, url: str) -> str:
        config.log_debug(f"Crawling page: {url}")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, timeout=30) as response:
                    content = await response.read()
                    try:
                        return content.decode('utf-8')
                    except:
                        try:
                            return content.decode('iso-8859-1')
                        except:
                            return content.decode('windows-1252', errors='ignore')
            except Exception as e:
                config.log_debug(f"Error crawling page: {e}")
                return ""
    
    async def extract_products(self, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, 'lxml')
        products = []
        
        # Look for product items
        product_items = soup.find_all('li')
        
        for item in product_items:
            # Check if this is a product by looking for product link
            product_link = item.find('a', href=re.compile(r'/brindes/brinde\.asp\?id=\d+'))
            if product_link:
                try:
                    product = self._extract_product_info(item)
                    if product:
                        products.append(product)
                except Exception as e:
                    config.log_debug(f"Error extracting product: {e}")
        
        config.log_debug(f"Extracted {len(products)} products from page")
        return products
    
    async def extract_categories(self, html: str) -> List[Dict[str, Any]]:
        # Return pre-defined categories
        categories = []
        for cat_id, cat_info in self.categories_structure.items():
            categories.append({
                "id": cat_id,
                "name": cat_info["name"],
                "url": f"/brindes/categoria.asp?idCategoria={cat_id}",
                "subcategories": cat_info["subcategories"]
            })
        return categories
    
    def _extract_product_info(self, item) -> Optional[Dict[str, Any]]:
        try:
            # Find all product links
            links = item.find_all('a', href=re.compile(r'/brindes/brinde\.asp\?id=\d+'))
            if not links:
                return None
            
            # Extract product ID
            href = links[0].get('href', '')
            id_match = re.search(r'id=(\d+)', href)
            if not id_match:
                return None
            
            product_id = id_match.group(1)
            
            # Extract name
            name_text = ""
            for link in links:
                text = link.get_text(strip=True)
                if text and not text.startswith('http'):
                    name_text = text
                    break
            
            if not name_text:
                return None
            
            # Extract price
            price = None
            price_text = item.get_text()
            price_patterns = [
                r'Desde\s+(\d+[.,]\d+)\s*€',
                r'(\d+[.,]\d+)\s*€',
                r'€\s*(\d+[.,]\d+)'
            ]
            
            for pattern in price_patterns:
                price_match = re.search(pattern, price_text)
                if price_match:
                    price = float(price_match.group(1).replace(',', '.'))
                    break
            
            # Extract reference
            ref_match = re.search(r'[A-Z]{2,}\d{3,}', price_text)
            reference = ref_match.group(0) if ref_match else None
            
            return {
                'id': product_id,
                'name': name_text,
                'url': f"{self.base_url}/brindes/brinde.asp?id={product_id}",
                'price': price,
                'reference': reference
            }
        except Exception as e:
            config.log_debug(f"Error extracting product info: {e}")
            return None
    
    def build_filter_url(self, category_id: int, subcategory_id: Optional[int] = None, 
                        color: Optional[str] = None, price_min: Optional[float] = None,
                        price_max: Optional[float] = None, search_query: Optional[str] = None) -> str:
        """Build a proper filter URL for Signa website"""
        
        params = {
            'q': search_query or '',
            't': '',
            'idCategoria': str(category_id),
            'idSubCategoria': str(subcategory_id) if subcategory_id else '',
            'idOcasiao': '',
            'idSector': '',
            'idCorPrincipal': '',
            'precoDe': str(price_min) if price_min else '',
            'precoAte': str(price_max) if price_max else '',
            'idMaterial': '',
            'idDimensao': '',
            'idGramagem': '',
            'idCapacidade': '',
            'idCapacidadePB': '',
            'corDaEscrita': '',
            'order': '',
            'prodPorPagina': '25'
        }
        
        # Map color name to ID
        if color:
            color_lower = color.lower()
            if color_lower in self.color_map:
                params['idCorPrincipal'] = self.color_map[color_lower]
        
        # Build URL
        query_string = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"{self.base_url}/brindes/categoria.asp?{query_string}"