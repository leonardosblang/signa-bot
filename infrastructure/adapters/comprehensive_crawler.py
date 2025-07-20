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
        
       
        self.color_map = {
            'preto': '72',
            'preta': '72',
            'pretos': '72',
            'pretas': '72',
            'black': '72',
            'cinzento': '259',
            'cinza': '259',
            'cinzentos': '259',
            'cinzas': '259',
            'grey': '259',
            'gray': '259',
            'prata': '325',
            'prateado': '325',
            'prateada': '325',
            'prateados': '325',
            'prateadas': '325',
            'silver': '325',
            'roxo': '108',
            'roxa': '108',
            'roxos': '108',
            'roxas': '108',
            'purple': '108',
            'violeta': '108',
            'azul': '117',
            'azuis': '117',
            'blue': '117',
            'rosa': '106',
            'rosas': '106',
            'pink': '106',
            'verde': '96',
            'verdes': '96',
            'green': '96',
            'vermelho': '103',
            'vermelha': '103',
            'vermelhos': '103',
            'vermelhas': '103',
            'red': '103',
            'laranja': '87',
            'laranjas': '87',
            'orange': '87',
            'castanho': '91',
            'castanha': '91',
            'marrom': '91',
            'brown': '91',
            'amarelo': '82',
            'amarela': '82',
            'amarelos': '82',
            'amarelas': '82',
            'yellow': '82',
            'bege': '321',
            'beges': '321',
            'natural': '321',
            'branco': '62',
            'branca': '62',
            'brancos': '62',
            'brancas': '62',
            'white': '62'
        }
        
        self.categories_structure = {
            44: {"name": "Beleza & Saúde", "subcategories": [
                {"id": 359, "name": "Bálsamos Labial"},
                {"id": 262, "name": "Caixas de Comprimidos"},
                {"id": 258, "name": "Cuidado Pessoal"},
                {"id": 360, "name": "Escovas & Escovas de Dentes"},
                {"id": 263, "name": "Espelhos"},
                {"id": 265, "name": "Massajadores"}
            ]},
            32: {"name": "Bricolage & Auto", "subcategories": [
                {"id": 201, "name": "Acessórios de Viatura"},
                {"id": 194, "name": "Canivetes & Navalhas"},
                {"id": 193, "name": "Ferramentas"},
                {"id": 195, "name": "Fitas Métricas"},
                {"id": 199, "name": "Jardinagem"},
                {"id": 196, "name": "Lanternas & Luzes"},
                {"id": 202, "name": "Lupas Conta-fios & Escalímetros"},
                {"id": 323, "name": "Para-Sol para Automóveis"},
                {"id": 198, "name": "Pilhas & Carregadores"},
                {"id": 197, "name": "X-actos"}
            ]},
            30: {"name": "Casa & Lar", "subcategories": [
                {"id": 175, "name": "Abre-cápsulas & Saca-rolhas"},
                {"id": 173, "name": "Acessórios p/ Bebidas"},
                {"id": 164, "name": "Canecas Personalizadas"},
                {"id": 171, "name": "Chávenas de Chá & Café"},
                {"id": 172, "name": "Copos & Pratos"},
                {"id": 312, "name": "Decorações & Enfeites"},
                {"id": 168, "name": "Kits Emergência & Sobrevivência"},
                {"id": 301, "name": "Lancheiras & Frascos"},
                {"id": 178, "name": "Luvas & Pegas"},
                {"id": 176, "name": "Mantas"},
                {"id": 300, "name": "Mealheiros"},
                {"id": 356, "name": "Tábuas de Servir"},
                {"id": 307, "name": "Toalhas & Panos"},
                {"id": 170, "name": "Utilidades"},
                {"id": 166, "name": "Velas & Ambientadores"}
            ]},
            34: {"name": "Doces", "subcategories": [
                {"id": 215, "name": "Caixinhas & Potes"},
                {"id": 212, "name": "Chocolates Personalizados"},
                {"id": 217, "name": "Chupa-chupas"},
                {"id": 214, "name": "Gomas"},
                {"id": 213, "name": "Rebuçados & Caramelos"}
            ]},
            35: {"name": "Escrita & Escritório", "subcategories": [
                {"id": 222, "name": "Agendas Personalizadas"},
                {"id": 221, "name": "Blocos de Notas"},
                {"id": 313, "name": "Borrachas & Afias"},
                {"id": 289, "name": "Calculadoras"},
                {"id": 223, "name": "Calendários & Relógios"},
                {"id": 304, "name": "Clips & Molas"},
                {"id": 236, "name": "Conjuntos de Escrita"},
                {"id": 219, "name": "Esferográficas"},
                {"id": 232, "name": "Estojos & Porta-Lápis"},
                {"id": 220, "name": "Lápis & Lapiseiras"},
                {"id": 225, "name": "Luzes, Lâmpadas & Lasers"},
                {"id": 306, "name": "Marcadores"},
                {"id": 233, "name": "Material de Secretária"},
                {"id": 224, "name": "Notas Adesivas & Lembretes"},
                {"id": 229, "name": "Pastas & Porta-documentos"},
                {"id": 243, "name": "Pastas e Mochilas para Portáteis"},
                {"id": 325, "name": "Réguas"},
                {"id": 227, "name": "Tapetes de Rato"}
            ]},
            33: {"name": "Identificadores", "subcategories": [
                {"id": 209, "name": "Crachás"},
                {"id": 207, "name": "Fitas Lanyard"},
                {"id": 302, "name": "Ímans"},
                {"id": 208, "name": "Pins Personalizados"},
                {"id": 206, "name": "Pulseiras Personalizadas"}
            ]},
            39: {"name": "Lazer", "subcategories": [
                {"id": 309, "name": "Animais"},
                {"id": 299, "name": "Ar Livre"},
                {"id": 342, "name": "Bolas"},
                {"id": 361, "name": "Desporto"},
                {"id": 177, "name": "Garrafas Personalizadas"},
                {"id": 275, "name": "Insufláveis"},
                {"id": 269, "name": "Jogos & Puzzles"},
                {"id": 297, "name": "Leques"},
                {"id": 358, "name": "Mundo da Criança"},
                {"id": 328, "name": "Peluches"},
                {"id": 272, "name": "Verão & Praia"},
                {"id": 357, "name": "Viagens"}
            ]},
            38: {"name": "Pessoais", "subcategories": [
                {"id": 260, "name": "Anti-stress"},
                {"id": 261, "name": "Carteiras & Porta-Cartões"},
                {"id": 256, "name": "Isqueiros"},
                {"id": 324, "name": "Medalhas & Troféus"},
                {"id": 242, "name": "Necessaires"},
                {"id": 257, "name": "Óculos"},
                {"id": 255, "name": "Porta-Chaves Personalizados"},
                {"id": 259, "name": "Relógios"}
            ]},
            37: {"name": "Sacos & Mochilas", "subcategories": [
                {"id": 238, "name": "Bolsas"},
                {"id": 253, "name": "Caixas"},
                {"id": 254, "name": "Carrinhos de Compras"},
                {"id": 237, "name": "Malas & Trolleys"},
                {"id": 241, "name": "Mochilas"},
                {"id": 349, "name": "Sacos de Algodão"},
                {"id": 251, "name": "Sacos de Compras"},
                {"id": 250, "name": "Sacos de Pano"},
                {"id": 248, "name": "Sacos de Papel"},
                {"id": 244, "name": "Sacos Desporto"},
                {"id": 239, "name": "Sacos Dobráveis"},
                {"id": 298, "name": "Sacos e Lancheiras Térmicas"},
                {"id": 315, "name": "Sacos em Non Woven"},
                {"id": 362, "name": "Sacos para Garrafas"},
                {"id": 350, "name": "Sacos Tipo Mochila"}
            ]},
            40: {"name": "Suportes Publicitários", "subcategories": [
                {"id": 284, "name": "Acrílicos Porta-Folhas"},
                {"id": 278, "name": "Balcões"},
                {"id": 277, "name": "Bandeiras de Publicidade"},
                {"id": 281, "name": "Banners"},
                {"id": 347, "name": "Cartões de Visita, Flyers & Outros"},
                {"id": 285, "name": "Cavaletes & Expositores de Exterior"},
                {"id": 288, "name": "Gestores de Fila"},
                {"id": 282, "name": "Muros Pop-Up e Tecido"},
                {"id": 348, "name": "Packs Promocionais"},
                {"id": 286, "name": "Porta-catálogos"},
                {"id": 283, "name": "Roll-Ups"},
                {"id": 346, "name": "Snap Frames"},
                {"id": 279, "name": "Tendas"}
            ]},
            41: {"name": "Tecnologia", "subcategories": [
                {"id": 234, "name": "Acessórios p/ Telemóveis & Tabletes"},
                {"id": 296, "name": "Adaptadores"},
                {"id": 351, "name": "Carregadores & Powerbanks"},
                {"id": 294, "name": "Cartões de Memórias"},
                {"id": 345, "name": "Colunas & Auriculares"},
                {"id": 226, "name": "Extensões & Acessórios USB"},
                {"id": 310, "name": "Máquinas Fotográficas"},
                {"id": 293, "name": "Pens USB Personalizadas"},
                {"id": 316, "name": "Ratos"},
                {"id": 290, "name": "Web Cam"}
            ]},
            31: {"name": "Vestuário", "subcategories": [
                {"id": 191, "name": "Acessórios"},
                {"id": 188, "name": "Aventais"},
                {"id": 179, "name": "Bonés, Chapéus & Panamás"},
                {"id": 318, "name": "Calçado"},
                {"id": 185, "name": "Calças e Calções"},
                {"id": 334, "name": "Camisas"},
                {"id": 184, "name": "Camisolas & Sweatshirts"},
                {"id": 190, "name": "Capas & Ponchos"},
                {"id": 187, "name": "Casacos & Blusões"},
                {"id": 192, "name": "Chinelos Personalizados"},
                {"id": 183, "name": "Coletes"},
                {"id": 333, "name": "Fatos Treino"},
                {"id": 343, "name": "Gorros e Luvas"},
                {"id": 180, "name": "Gravatas, Lenços & Cachecóis"},
                {"id": 189, "name": "Guarda-chuvas"},
                {"id": 332, "name": "Polares"},
                {"id": 182, "name": "Polos Personalizados"},
                {"id": 247, "name": "Porta-fatos e gravatas"},
                {"id": 181, "name": "T-Shirts Personalizadas"},
                {"id": 321, "name": "Vestuário de Alta Visibilidade"},
                {"id": 186, "name": "Vestuário de Trabalho"}
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