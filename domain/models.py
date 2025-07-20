from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum

class ProductCategory(Enum):
    BELEZA_SAUDE = 1
    BRICOLAGE_AUTO = 2
    CASA_LAR = 3
    DESKTOP = 4
    DOCES_ALIMENTACAO = 5
    ESCRITA_ESCRITORIO = 6
    MALAS_VIAGEM = 7
    OUTDOORS = 8
    PORTA_CHAVES = 9
    TECNOLOGIA = 10
    TEXTIL_CHAPEUS = 11
    VERAO = 12
    VESTUARIO = 13

@dataclass
class Product:
    id: str
    name: str
    category: str
    subcategory: Optional[str]
    price: Optional[float]
    colors: List[str]
    url: str
    description: Optional[str]
    
@dataclass
class CategoryInfo:
    id: int
    name: str
    subcategories: List[Dict[str, Any]]
    url: str
    
@dataclass
class ChatMessage:
    role: str
    content: str
    
@dataclass
class SearchQuery:
    text: str
    category: Optional[str]
    color: Optional[str]
    price_min: Optional[float]
    price_max: Optional[float]
    
@dataclass
class SearchResult:
    products: List[Product]
    category_url: Optional[str]
    filter_url: Optional[str]
    message: str