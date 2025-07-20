import json
import os
from typing import List, Dict, Any, Optional
from ports.knowledge_base_port import KnowledgeBasePort
from infrastructure.config import config
import re
from fuzzywuzzy import fuzz
import pickle

class InMemoryKnowledgeBase(KnowledgeBasePort):
    def __init__(self):
        self.products = []
        self.categories = []
        self.category_map = {}
        self.product_map = {}
        self.data_file = "knowledge_base.pkl"
        self._load_data()
        
    async def store_products(self, products: List[Dict[str, Any]]) -> None:
        config.log_debug(f"Storing {len(products)} products")
        
        for product in products:
            if product.get('id') and product['id'] not in self.product_map:
                self.products.append(product)
                self.product_map[product['id']] = product
                
        self._save_data()
    
    async def store_categories(self, categories: List[Dict[str, Any]]) -> None:
        config.log_debug(f"Storing {len(categories)} categories")
        
        self.categories = categories
        self.category_map = {cat['name'].lower(): cat for cat in categories}
        
        for cat in categories:
            if 'id' in cat:
                self.category_map[str(cat['id'])] = cat
                
        self._save_data()
    
    async def search_products(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        config.log_debug(f"Searching products with query: {query}, filters: {filters}")
        
        results = []
        query_lower = query.lower() if query else ""
        
        if filters is None:
            filters = {}
        
        for product in self.products:
            if query_lower:
                score = self._calculate_match_score(product, query_lower)
            else:
                score = 100  # If no query, match all
            
            if score > 60:
                if self._apply_filters(product, filters):
                    product_copy = product.copy()
                    product_copy['match_score'] = score
                    results.append(product_copy)
        
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
        return results[:20]
    
    async def get_category_info(self, category_name: str) -> Optional[Dict[str, Any]]:
        config.log_debug(f"Getting category info for: {category_name}")
        
        category_lower = category_name.lower()
        
        if category_lower in self.category_map:
            return self.category_map[category_lower]
        
        for name, cat in self.category_map.items():
            if isinstance(name, str) and fuzz.ratio(category_lower, name) > 80:
                return cat
                
        for cat in self.categories:
            if fuzz.ratio(category_lower, cat['name'].lower()) > 80:
                return cat
                
        return None
    
    async def get_all_data(self) -> Dict[str, Any]:
        return {
            "products": self.products,
            "categories": self.categories,
            "total_products": len(self.products),
            "total_categories": len(self.categories)
        }
    
    def _calculate_match_score(self, product: Dict[str, Any], query: str) -> int:
        name_score = fuzz.partial_ratio(query, product['name'].lower())
        
        category_score = 0
        if product.get('category'):
            category_score = fuzz.partial_ratio(query, product['category'].lower())
        
        exact_match_bonus = 0
        if query in product['name'].lower():
            exact_match_bonus = 20
        
        return max(name_score, category_score) + exact_match_bonus
    
    def _apply_filters(self, product: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        if 'color' in filters and filters['color']:
            if not product.get('colors'):
                return False
            color_match = any(fuzz.ratio(filters['color'].lower(), color.lower()) > 70 
                            for color in product['colors'])
            if not color_match:
                return False
        
        if 'price_min' in filters and filters['price_min'] is not None:
            if not product.get('price') or product['price'] < filters['price_min']:
                return False
                
        if 'price_max' in filters and filters['price_max'] is not None:
            if not product.get('price') or product['price'] > filters['price_max']:
                return False
        
        if 'category' in filters and filters['category']:
            if not product.get('category'):
                return False
            if fuzz.ratio(filters['category'].lower(), product['category'].lower()) < 70:
                return False
        
        return True
    
    def _save_data(self):
        try:
            with open(self.data_file, 'wb') as f:
                pickle.dump({
                    'products': self.products,
                    'categories': self.categories,
                    'category_map': self.category_map,
                    'product_map': self.product_map
                }, f)
            config.log_debug(f"Data saved to {self.data_file}")
        except Exception as e:
            config.log_debug(f"Error saving data: {e}")
    
    def _load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'rb') as f:
                    data = pickle.load(f)
                    self.products = data.get('products', [])
                    self.categories = data.get('categories', [])
                    self.category_map = data.get('category_map', {})
                    self.product_map = data.get('product_map', {})
                config.log_debug(f"Data loaded from {self.data_file}")
            except Exception as e:
                config.log_debug(f"Error loading data: {e}")