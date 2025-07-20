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

### 2. Crawl4AI
- **Versão**: 0.7.x
- **Propósito**: Web crawling inteligente com suporte a IA e browser automation
- **Uso no projeto**:
  - `infrastructure/adapters/crawler_adapter.py`: Scraping principal do site Signa
  - `infrastructure/adapters/comprehensive_crawler.py`: Extração avançada de conteúdo
  - Browser automation via Playwright para sites dinâmicos
  - Extração inteligente de conteúdo com anti-detection

### 3. BeautifulSoup4
- **Versão**: 4.x
- **Propósito**: Parsing e extração de dados HTML (fallback)
- **Uso no projeto**:
  - `infrastructure/adapters/simple_crawler_adapter.py`: Scraping fallback
  - Processamento de HTML estático
  - Extração básica quando crawl4ai não está disponível

### 4. aiohttp
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

## Bibliotecas da Interface Gráfica

### 13. Streamlit
- **Versão**: 1.29.0+
- **Propósito**: Framework para interfaces web interativas
- **Uso no projeto**:
  - `presentation/web/app.py`: Interface web principal
  - Chat interface moderna
  - Exibição de produtos e resultados
  - Gestão de sessões de utilizador

### 14. FastAPI
- **Versão**: 0.104.0+
- **Propósito**: Framework web moderno para APIs
- **Uso no projeto**:
  - `presentation/api/main.py`: Servidor backend
  - Endpoints RESTful para comunicação
  - Validação automática de dados
  - Documentação automática (/docs)

### 15. Uvicorn
- **Versão**: 0.24.0+
- **Propósito**: Servidor ASGI de alta performance
- **Uso no projeto**:
  - `run_api.py`: Servidor para FastAPI
  - Suporte a WebSockets e HTTP/2
  - Auto-reload em desenvolvimento

### 16. httpx
- **Versão**: 0.25.0+
- **Propósito**: Cliente HTTP assíncrono
- **Uso no projeto**:
  - `presentation/web/app.py`: Comunicação Streamlit → API
  - Requisições assíncronas para melhor performance
  - Timeouts e retry configuráveis

### 17. Pydantic
- **Versão**: 2.5.0+
- **Propósito**: Validação de dados e settings
- **Uso no projeto**:
  - `presentation/api/models.py`: Modelos de dados da API
  - Validação automática de requests/responses
  - Serialização JSON automática

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
Todas as dependências são organizadas por categoria:

```
# Core AI & Web Scraping
openai>=1.50.0
crawl4ai[all]>=0.7.0
python-dotenv>=1.0.0
aiohttp>=3.9.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
tenacity>=8.2.0

# Data Processing & Matching
fuzzywuzzy>=0.18.0
python-Levenshtein>=0.25.0
pydantic>=2.5.0

# CLI Interface
colorama>=0.4.6

# API Interface
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
httpx>=0.25.0

# Web Interface
streamlit>=1.29.0

# Optional async support
nest-asyncio>=1.6.0
```

### Instalação
```bash
pip install -r requirements.txt
crawl4ai-setup  # Configurar navegadores
```

## Considerações de Performance

1. **crawl4ai + Playwright**: Browser automation eficiente com anti-detection
2. **aiohttp + asyncio**: Permite crawling paralelo eficiente
3. **lxml**: Parser mais rápido que html.parser
4. **python-Levenshtein**: Acelera fuzzy matching 4-10x
5. **Caching**: Reduz chamadas à API OpenAI
6. **Multi-interface**: CLI, API e Web podem correr em paralelo

## Segurança

- **python-dotenv**: Mantém credenciais fora do código
- **pydantic**: Validação previne injeção de dados
- **Sanitização**: BeautifulSoup previne XSS em scraping