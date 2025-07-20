import openai
from typing import List, Optional, Dict, Any
from ports.chatbot_port import ChatbotPort
from ports.knowledge_base_port import KnowledgeBasePort
from domain.models import ChatMessage, SearchResult, SearchQuery
from infrastructure.config import config
from infrastructure.adapters.comprehensive_crawler import ComprehensiveCrawlerAdapter
import re
import json

class IntelligentChatbotAdapter(ChatbotPort):
    def __init__(self, knowledge_base: KnowledgeBasePort):
        self.knowledge_base = knowledge_base
        openai.api_key = config.openai_api_key
        self.model = config.openai_model
        self.crawler = ComprehensiveCrawlerAdapter()
        
    async def process_message(self, message: str, context: Optional[List[ChatMessage]] = None) -> str:
        config.log_debug(f"Processing message: {message}")
        
        # Analyze and correct typos using LLM
        query_info = await self._analyze_and_correct_query(message)
        
        if query_info['type'] == 'product_search':
            return await self._handle_product_search(query_info['corrected_message'], query_info)
        elif query_info['type'] == 'company_info':
            return await self._get_company_info(message)
        else:
            return await self._general_response(message, context)
    
    async def _analyze_and_correct_query(self, message: str) -> Dict[str, Any]:
        """Use LLM to understand query intent and correct typos"""
        
        prompt = f"""Analise a seguinte pergunta sobre produtos da loja Signa. 
IMPORTANTE: Corrija erros de digitação e entenda a intenção real do usuário.

Pergunta original: "{message}"

Correções comuns:
- "bones" ou "bonnes" → "bonés" 
- "camisa" → pode ser "camisas" ou "t-shirts"
- "marcador" → "marcadores"
- "caneca azuis" → "canecas azuis"
- "mochilla" → "mochila"
- "porwer bank" → "powerbank"
- "porta chave" → "porta-chaves"
- "tshirt" → "t-shirt"
- "pen drive" → "pen drives"
- "bolca" → "bolsa"

Produtos disponíveis na Signa:
- Canecas, Copos, Garrafas, Termos
- Canetas, Lápis, Marcadores, Cadernos
- Mochilas, Bolsas, Sacos
- T-Shirts, Polos, Camisas, Sweatshirts, Casacos, Bonés, Chapéus
- PowerBanks, Pen Drives, Auriculares, Colunas
- Porta-Chaves, Lanyards, Pins
- Produtos de beleza, bricolage, doces, lazer

Retorne um JSON com:
- type: "product_search", "company_info", ou "general"
- corrected_message: mensagem corrigida (se houver typos)
- product: produto procurado (corrigido)
- category: categoria do produto
- color: cor (se mencionada) - valores aceitos: azul, vermelho, verde, preto, branco, amarelo, laranja, rosa, cinza, castanho, roxo, dourado, prateado, etc.
- price_min: preço mínimo (se mencionado)
- price_max: preço máximo (se mencionado)

Exemplos:
- "tem bones azuis?" → corrected_message: "tem bonés azuis?", product: "bonés", color: "azul"
- "marcador verde" → corrected_message: "marcadores verdes", product: "marcadores", color: "verde"
- "camisa preta" → corrected_message: "camisas pretas", product: "camisas", color: "preto"
"""
        
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "És um assistente inteligente que corrige erros de digitação e entende intenções."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Log corrections made
            if result.get('corrected_message') and result['corrected_message'] != message:
                config.log_debug(f"Corrected '{message}' to '{result['corrected_message']}'")
                
            return result
            
        except Exception as e:
            config.log_debug(f"Error analyzing query: {e}")
            # Fallback without correction
            return {
                'type': 'product_search',
                'corrected_message': message,
                'product': message
            }
    
    async def _handle_product_search(self, message: str, query_info: Dict[str, Any]) -> str:
        """Handle product searches with intelligent matching"""
        
        # Get categories from knowledge base
        all_data = await self.knowledge_base.get_all_data()
        
        # Map product types to categories using corrected product name
        product_type = query_info.get('product', '').lower()
        color = query_info.get('color')
        
        # Comprehensive product mappings
        product_mappings = {
            # Casa & Lar (30)
            'caneca': {'cat': 30, 'subcat': 164, 'name': 'canecas'},
            'canecas': {'cat': 30, 'subcat': 164, 'name': 'canecas'},
            'copo': {'cat': 30, 'subcat': 165, 'name': 'copos'},
            'copos': {'cat': 30, 'subcat': 165, 'name': 'copos'},
            'garrafa': {'cat': 30, 'subcat': 166, 'name': 'garrafas'},
            'garrafas': {'cat': 30, 'subcat': 166, 'name': 'garrafas'},
            'termo': {'cat': 30, 'subcat': 167, 'name': 'termos'},
            'termos': {'cat': 30, 'subcat': 167, 'name': 'termos'},
            
            # Escrita & Escritório (35)
            'caneta': {'cat': 35, 'subcat': 170, 'name': 'canetas'},
            'canetas': {'cat': 35, 'subcat': 170, 'name': 'canetas'},
            'lápis': {'cat': 35, 'subcat': 171, 'name': 'lápis'},
            'marcador': {'cat': 35, 'subcat': 172, 'name': 'marcadores'},
            'marcadores': {'cat': 35, 'subcat': 172, 'name': 'marcadores'},
            'caderno': {'cat': 35, 'subcat': 173, 'name': 'cadernos'},
            'cadernos': {'cat': 35, 'subcat': 173, 'name': 'cadernos'},
            'bloco': {'cat': 35, 'subcat': 174, 'name': 'blocos de notas'},
            'blocos': {'cat': 35, 'subcat': 174, 'name': 'blocos de notas'},
            
            # Sacos & Mochilas (37)
            'mochila': {'cat': 37, 'subcat': 159, 'name': 'mochilas'},
            'mochilas': {'cat': 37, 'subcat': 159, 'name': 'mochilas'},
            'bolsa': {'cat': 37, 'subcat': 141, 'name': 'bolsas'},
            'bolsas': {'cat': 37, 'subcat': 141, 'name': 'bolsas'},
            'saco': {'cat': 37, 'subcat': 180, 'name': 'sacos'},
            'sacos': {'cat': 37, 'subcat': 180, 'name': 'sacos'},
            
            # Tecnologia (41)
            'powerbank': {'cat': 41, 'subcat': 190, 'name': 'powerbanks'},
            'powerbanks': {'cat': 41, 'subcat': 190, 'name': 'powerbanks'},
            'power bank': {'cat': 41, 'subcat': 190, 'name': 'powerbanks'},
            'pen drive': {'cat': 41, 'subcat': 191, 'name': 'pen drives'},
            'pen drives': {'cat': 41, 'subcat': 191, 'name': 'pen drives'},
            'pendrive': {'cat': 41, 'subcat': 191, 'name': 'pen drives'},
            'pendrives': {'cat': 41, 'subcat': 191, 'name': 'pen drives'},
            'auricular': {'cat': 41, 'subcat': 192, 'name': 'auriculares'},
            'auriculares': {'cat': 41, 'subcat': 192, 'name': 'auriculares'},
            'fone': {'cat': 41, 'subcat': 192, 'name': 'auriculares'},
            'fones': {'cat': 41, 'subcat': 192, 'name': 'auriculares'},
            'coluna': {'cat': 41, 'subcat': 193, 'name': 'colunas'},
            'colunas': {'cat': 41, 'subcat': 193, 'name': 'colunas'},
            
            # Vestuário (31)
            't-shirt': {'cat': 31, 'subcat': 200, 'name': 't-shirts'},
            't-shirts': {'cat': 31, 'subcat': 200, 'name': 't-shirts'},
            'tshirt': {'cat': 31, 'subcat': 200, 'name': 't-shirts'},
            'tshirts': {'cat': 31, 'subcat': 200, 'name': 't-shirts'},
            'camiseta': {'cat': 31, 'subcat': 200, 'name': 't-shirts'},
            'camisetas': {'cat': 31, 'subcat': 200, 'name': 't-shirts'},
            'camisa': {'cat': 31, 'subcat': 202, 'name': 'camisas'},
            'camisas': {'cat': 31, 'subcat': 202, 'name': 'camisas'},
            'polo': {'cat': 31, 'subcat': 201, 'name': 'polos'},
            'polos': {'cat': 31, 'subcat': 201, 'name': 'polos'},
            'sweatshirt': {'cat': 31, 'subcat': 203, 'name': 'sweatshirts'},
            'sweatshirts': {'cat': 31, 'subcat': 203, 'name': 'sweatshirts'},
            'casaco': {'cat': 31, 'subcat': 204, 'name': 'casacos'},
            'casacos': {'cat': 31, 'subcat': 204, 'name': 'casacos'},
            'boné': {'cat': 31, 'subcat': 205, 'name': 'bonés'},
            'bonés': {'cat': 31, 'subcat': 205, 'name': 'bonés'},
            'bone': {'cat': 31, 'subcat': 205, 'name': 'bonés'},
            'bones': {'cat': 31, 'subcat': 205, 'name': 'bonés'},
            'chapéu': {'cat': 31, 'subcat': 206, 'name': 'chapéus'},
            'chapéus': {'cat': 31, 'subcat': 206, 'name': 'chapéus'},
            'chapeu': {'cat': 31, 'subcat': 206, 'name': 'chapéus'},
            
            # Identificadores (33)
            'porta-chaves': {'cat': 33, 'subcat': 175, 'name': 'porta-chaves'},
            'porta chaves': {'cat': 33, 'subcat': 175, 'name': 'porta-chaves'},
            'porta chave': {'cat': 33, 'subcat': 175, 'name': 'porta-chaves'},
            'chaveiro': {'cat': 33, 'subcat': 175, 'name': 'porta-chaves'},
            'chaveiros': {'cat': 33, 'subcat': 175, 'name': 'porta-chaves'},
            'lanyard': {'cat': 33, 'subcat': 176, 'name': 'lanyards'},
            'lanyards': {'cat': 33, 'subcat': 176, 'name': 'lanyards'},
            'pin': {'cat': 33, 'subcat': 177, 'name': 'pins'},
            'pins': {'cat': 33, 'subcat': 177, 'name': 'pins'},
            
            # Other categories
            'doce': {'cat': 34, 'name': 'doces'},
            'doces': {'cat': 34, 'name': 'doces'},
            'chocolate': {'cat': 34, 'name': 'chocolates'},
            'chocolates': {'cat': 34, 'name': 'chocolates'},
            'beleza': {'cat': 44, 'name': 'produtos de beleza'},
            'saúde': {'cat': 44, 'name': 'produtos de saúde'},
            'bricolage': {'cat': 32, 'name': 'produtos de bricolage'},
            'ferramenta': {'cat': 32, 'name': 'ferramentas'},
            'ferramentas': {'cat': 32, 'name': 'ferramentas'}
        }
        
        # Find matching product
        category_id = None
        subcategory_id = None
        category_name = product_type
        
        for keyword, mapping in product_mappings.items():
            if keyword in product_type:
                category_id = mapping['cat']
                subcategory_id = mapping.get('subcat')
                category_name = mapping['name']
                break
        
        # Build URL with filters
        if category_id:
            url = self.crawler.build_filter_url(
                category_id=category_id,
                subcategory_id=subcategory_id,
                color=color,
                price_min=query_info.get('price_min'),
                price_max=query_info.get('price_max')
            )
            
            # Build response
            response_parts = []
            
            if query_info.get('corrected_message') and query_info['corrected_message'] != message:
                response_parts.append(f"Entendi que procura: {query_info['corrected_message']}")
            
            if color:
                response_parts.append(f"Pode encontrar {category_name} {color}s aqui: {url}")
            else:
                response_parts.append(f"Pode encontrar {category_name} aqui: {url}")
                
            return "\n".join(response_parts)
        
        # If no category found, search in knowledge base
        search_query = SearchQuery(
            text=product_type or message,
            category=None,
            color=color,
            price_min=query_info.get('price_min'),
            price_max=query_info.get('price_max')
        )
        
        result = await self.search_products(search_query)
        return result.message
    
    async def search_products(self, query: SearchQuery) -> SearchResult:
        """Search products in knowledge base"""
        filters = {}
        if query.color:
            filters['color'] = query.color
        if query.price_min is not None:
            filters['price_min'] = query.price_min
        if query.price_max is not None:
            filters['price_max'] = query.price_max
            
        products = await self.knowledge_base.search_products(query.text, filters)
        
        if products:
            message_parts = [f"Encontrei {len(products)} produtos:"]
            for i, product in enumerate(products[:5]):
                message_parts.append(f"{i+1}. {product['name']} - {product['url']}")
            
            if len(products) > 5:
                message_parts.append(f"...e mais {len(products) - 5} produtos.")
                
            return SearchResult(
                products=products,
                category_url=None,
                filter_url=None,
                message="\n".join(message_parts)
            )
        
        # Try to build a search URL
        search_url = f"https://www.signa.pt/brindes/pesquisa.asp?q={query.text or ''}"
        return SearchResult(
            products=[],
            category_url=None,
            filter_url=search_url,
            message=f"Não encontrei produtos específicos. Tente pesquisar aqui: {search_url}"
        )
    
    async def get_product_by_id(self, product_id: str) -> Optional[dict]:
        all_data = await self.knowledge_base.get_all_data()
        for product in all_data.get('products', []):
            if product.get('id') == product_id:
                return product
        return None
    
    async def _get_company_info(self, message: str) -> str:
        """Get information about Signa company"""
        all_data = await self.knowledge_base.get_all_data()
        
        prompt = f"""És um assistente virtual da Signa, uma empresa portuguesa de brindes promocionais.
        
Informações sobre a Signa:
- Fundada em 2004 em Braga, Portugal
- Especializada em merchandising promocional e brindes personalizados
- Mais de 20.000 produtos disponíveis
- Oferece personalização de produtos (serigrafia, bordado, gravação laser, etc.)
- Amostras e mockups gratuitos
- Envio para toda Portugal e exportação
- Categorias principais: {', '.join([cat['name'] for cat in all_data.get('categories', [])])}

Pergunta do cliente: {message}

Responde de forma útil, profissional e amigável em português."""

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "És um assistente virtual especializado da Signa."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            config.log_debug(f"Error getting company info: {e}")
            return "Desculpe, ocorreu um erro ao processar sua pergunta."
    
    async def _general_response(self, message: str, context: Optional[List[ChatMessage]]) -> str:
        """Handle general queries"""
        messages = [
            {"role": "system", "content": "És um assistente virtual da Signa, especializada em brindes promocionais. Responde sempre em português de forma profissional e amigável."}
        ]
        
        if context:
            for msg in context[-5:]:
                messages.append({"role": msg.role, "content": msg.content})
                
        messages.append({"role": "user", "content": message})
        
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            config.log_debug(f"Error in general response: {e}")
            return "Desculpe, ocorreu um erro ao processar sua pergunta."