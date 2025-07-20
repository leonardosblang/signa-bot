# Bibliotecas Utilizadas

## Visão Geral

Este documento descreve todas as bibliotecas Python utilizadas no projeto Signa Chatbot, explicando o propósito de cada uma e onde são aplicadas.

## Bibliotecas Principais

### 1. OpenAI
- **Versão**: Latest
- **Propósito**: Integração com API GPT para processamento de linguagem natural
- **Uso no projeto**:
  - `infrastructure/adapters/chatbot_adapter.py`: Análise de queries e geração de respostas
  - Extração de intenções (produto, cor, categoria)
  - Processamento contextual de conversas

### 2. BeautifulSoup4
- **Versão**: 4.x
- **Propósito**: Parsing e extração de dados HTML
- **Uso no projeto**:
  - `infrastructure/adapters/simple_crawler_adapter.py`: Scraping do site Signa
  - Extração de produtos, categorias e metadados
  - Processamento de estruturas HTML complexas

### 3. aiohttp
- **Versão**: 3.x
- **Propósito**: Requisições HTTP assíncronas
- **Uso no projeto**:
  - `infrastructure/adapters/simple_crawler_adapter.py`: Download de páginas web
  - Gestão de timeouts e retries
  - Requisições paralelas para melhor performance

### 4. lxml
- **Versão**: Latest
- **Propósito**: Parser XML/HTML de alta performance
- **Uso no projeto**:
  - Backend para BeautifulSoup
  - Processamento eficiente de HTML
  - Suporte a seletores CSS complexos

## Bibliotecas de Suporte

### 5. python-dotenv
- **Versão**: Latest
- **Propósito**: Carregamento de variáveis de ambiente
- **Uso no projeto**:
  - `infrastructure/config.py`: Gestão de configurações
  - Carregamento seguro de API keys
  - Configurações por ambiente

### 6. colorama
- **Versão**: Latest
- **Propósito**: Cores no terminal (cross-platform)
- **Uso no projeto**:
  - `main.py`: Interface CLI colorida
  - Destaque de mensagens importantes
  - Melhor experiência de utilizador

### 7. pydantic
- **Versão**: 2.x
- **Propósito**: Validação de dados e settings
- **Uso no projeto**:
  - `infrastructure/utils/config.py`: Validação de configurações
  - Type hints e validação automática
  - Gestão de configurações tipadas

### 8. tenacity
- **Versão**: Latest
- **Propósito**: Retry logic com backoff
- **Uso no projeto**:
  - Retry em requisições HTTP falhadas
  - Gestão de rate limits
  - Resiliência em operações de rede

### 9. fuzzywuzzy
- **Versão**: Latest
- **Propósito**: Fuzzy string matching
- **Uso no projeto**:
  - `infrastructure/adapters/knowledge_base_adapter.py`: Pesquisa aproximada
  - Matching de cores e produtos similares
  - Tolerância a erros de digitação

### 10. python-Levenshtein
- **Versão**: Latest
- **Propósito**: Aceleração para fuzzywuzzy
- **Uso no projeto**:
  - Performance melhorada em string matching
  - Cálculo eficiente de distância entre strings

## Bibliotecas Assíncronas

### 11. nest-asyncio
- **Versão**: Latest
- **Propósito**: Permite asyncio em ambientes nested
- **Uso no projeto**:
  - Compatibilidade com Jupyter notebooks
  - Gestão de event loops aninhados
  - Suporte a diferentes ambientes

### 12. asyncio
- **Versão**: Built-in
- **Propósito**: Programação assíncrona
- **Uso no projeto**:
  - Todo o fluxo principal é assíncrono
  - Crawling paralelo de múltiplas páginas
  - Respostas não-bloqueantes

## Dependências Opcionais

### crawl4ai (Opcional)
- **Propósito**: Web scraping avançado com IA
- **Uso no projeto**:
  - Fallback para SimpleCrawlerAdapter se não disponível
  - Extração inteligente de conteúdo
  - Melhor handling de sites dinâmicos

## Estrutura de Imports

### Exemplo típico de imports no projeto:

```python
# infrastructure/adapters/chatbot_adapter.py
import openai                    # API OpenAI
from typing import List, Dict    # Type hints
import re                        # Regex para parsing
import json                      # Parsing de respostas

# infrastructure/adapters/simple_crawler_adapter.py
import aiohttp                   # HTTP assíncrono
from bs4 import BeautifulSoup    # HTML parsing
import asyncio                   # Async/await
from tenacity import retry       # Retry logic
```

## Gestão de Dependências

### requirements.txt
Todas as dependências são geridas através do ficheiro `requirements.txt`:

```
openai
python-dotenv
colorama
aiohttp
nest-asyncio
beautifulsoup4
lxml
pydantic
tenacity
fuzzywuzzy
python-Levenshtein
```

### Instalação
```bash
pip install -r requirements.txt
```

## Considerações de Performance

1. **aiohttp + asyncio**: Permite crawling paralelo eficiente
2. **lxml**: Parser mais rápido que html.parser
3. **python-Levenshtein**: Acelera fuzzy matching 4-10x
4. **Caching**: Reduz chamadas à API OpenAI

## Segurança

- **python-dotenv**: Mantém credenciais fora do código
- **pydantic**: Validação previne injeção de dados
- **Sanitização**: BeautifulSoup previne XSS em scraping