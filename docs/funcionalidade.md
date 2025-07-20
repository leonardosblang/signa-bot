# Funcionalidade do Signa Chatbot

## Visão Geral

O Signa Chatbot é um assistente virtual inteligente que ajuda utilizadores a encontrar produtos no catálogo da Signa, com capacidade de filtrar por cor, categoria e preço. O sistema oferece três interfaces diferentes para atender diversos casos de uso.

## Interfaces Disponíveis

### 1. Interface CLI (Linha de Comando)
```bash
python main.py
# ou
docker run -it signa-chatbot cli
```

**Características:**
- Interação via terminal
- Ideal para testes e desenvolvimento
- Suporte completo a todas as funcionalidades
- Logs detalhados em modo debug

**Comandos especiais:**
- `ajuda` - Lista comandos disponíveis
- `crawl` - Atualiza base de dados
- `stats` - Estatísticas do sistema
- `limpar` - Limpa histórico de conversa

### 2. API REST (FastAPI)
```bash
python run_api.py
# ou
docker run -p 8000:8000 signa-chatbot api
```

**Características:**
- Endpoint HTTP para integração
- Documentação automática em `/docs`
- Responses estruturados em JSON
- Ideal para integração com outros sistemas

**Endpoints principais:**
- `POST /chat` - Enviar mensagem ao chatbot
- `GET /health` - Status da aplicação
- `POST /crawl` - Forçar atualização de dados

### 3. Interface Web (Streamlit)
```bash
python run_web.py
# ou
docker run -p 8501:8501 signa-chatbot web
```

**Características:**
- Interface gráfica amigável
- Visualização rica de resultados
- Histórico de conversas
- Ideal para utilizadores finais

**Funcionalidades web:**
- Chat interativo
- Visualização de produtos com imagens
- Botões para ações rápidas
- Exportação de conversas

## Como Funciona

### 1. Fluxo Principal

```
Utilizador → Query → Análise IA → Pesquisa → Resposta com Links
```

1. **Entrada do Utilizador**: "tem caneca azul?"
2. **Análise por IA**: Extrai {produto: "caneca", cor: "azul"}
3. **Pesquisa na Base**: Procura produtos correspondentes
4. **Geração de Links**: Cria URLs com filtros aplicados
5. **Resposta**: Lista produtos + link de pesquisa filtrada

### 2. Processamento de Queries

#### Análise de Intenção
O chatbot identifica 3 tipos de queries:
- **product_search**: Pesquisa de produtos
- **company_info**: Informações sobre a Signa
- **general**: Conversação geral

#### Extração de Parâmetros
```python
Query: "mochila amarela barata"
↓
{
  "type": "product_search",
  "product": "mochila",
  "color": "amarela",
  "price_max": 20.0
}
```

### 3. Sistema de Pesquisa

#### Filtros Suportados
- **Texto**: Nome ou descrição do produto
- **Cor**: Mapeamento de cores para IDs
- **Categoria**: Filtro por tipo de produto
- **Preço**: Intervalo mínimo e máximo

#### Fuzzy Matching
- Tolerância a erros: "canecca" → "caneca"
- Similaridade: "bolsa" encontra "bolsas"
- Score mínimo: 80% de similaridade

## Web Scraper

### Arquitecturas de Crawling

O sistema utiliza múltiplas estratégias de web scraping para máxima eficácia:

#### 1. Crawl4AI (Principal)
```python
from crawl4ai import AsyncWebCrawler, BrowserConfig
```

**Características:**
- Browser automation com Playwright
- Suporte para JavaScript rendering
- Extração inteligente de conteúdo
- Anti-detection capabilities

**Configuração:**
```python
browser_config = BrowserConfig(
    headless=True,
    browser_type="chromium"
)
```

#### 2. BeautifulSoup (Fallback)
```python
from bs4 import BeautifulSoup
import aiohttp
```

**Características:**
- HTTP requests simples
- Parsing HTML estático
- Menor overhead de recursos
- Compatibilidade máxima

### Como Funciona o Crawler

#### 1. Descoberta de Categorias
```
signaplay.pt → Lista categorias → URLs de cada categoria
```

**Processo:**
1. Acede à página principal
2. Identifica links de categorias
3. Extrai metadados (nome, ID, URL)
4. Constrói mapa de navegação

#### 2. Extração de Produtos
```
Categoria → Páginas → Produtos → Detalhes
```

**Dados extraídos:**
- Nome do produto
- Preço e variações
- Cores disponíveis
- URLs de imagens
- Descrições
- URLs de produto

#### 3. Processamento de Dados
```python
HTML → Parser → Validation → KnowledgeBase
```

**Pipeline:**
1. Download da página
2. Parsing com crawl4ai/BeautifulSoup
3. Validação com Pydantic
4. Armazenamento estruturado

### Estratégias de Resiliência

#### Retry Logic Avançado
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
```

- Backoff exponencial
- Timeout configurável (30s padrão)
- Circuit breaker pattern
- Fallback para adapter alternativo

#### Sistema de Cache Inteligente
- **Persistência**: `knowledge_base.pkl`
- **TTL configurável**: 1-24 horas
- **Invalidação seletiva**: Por categoria
- **Compressão**: Dados otimizados

#### Fallback Hierárquico
```
Crawl4AI → BeautifulSoup → Dados Mock
```

1. **Crawl4AI**: Extração completa
2. **BeautifulSoup**: Extração básica
3. **Mock Data**: Dados exemplo para demonstração

### Configurações de Performance

#### Crawl4AI Otimizado
```python
# Configurações Docker
ENV CRAWL4AI_BROWSER_TYPE=chromium
ENV DISPLAY=:99
```

#### Controlo de Rate Limiting
- Delays entre requests
- Pool de connections limitado
- Headers user-agent rotativos

#### Monitorização
- Logs estruturados
- Métricas de performance
- Alertas de falhas

## Geração de Links

### URLs com Filtros

O sistema gera 2 tipos de URLs:

1. **Links de Produto Individual**
   ```
   https://www.signa.pt/brindes/brinde.asp?id=12345
   ```

2. **Links de Pesquisa Filtrada**
   ```
   https://www.signa.pt/brindes/pesquisa.asp?q=caneca&idCorPrincipal=6
   ```

### Mapeamento de Cores
```python
cores = {
    'amarelo': '6',
    'azul': '1',
    'vermelho': '2',
    'verde': '3',
    'preto': '4',
    'branco': '5'
}
```

## Interfaces Disponíveis

### 1. Interface Gráfica Web (Recomendada)
- **Tecnologia**: Streamlit + FastAPI
- **Acesso**: http://localhost:8501
- **Funcionalidades**:
  - Chat interface moderna
  - Exibição visual de produtos
  - Links diretos para compra
  - Exemplos de pesquisas
  - Histórico persistente

### 2. Interface CLI

#### Comandos Disponíveis
- **ajuda**: Mostra comandos e exemplos
- **stats**: Estatísticas da base de dados
- **crawl**: Atualiza dados do site
- **limpar**: Limpa histórico de conversa
- **sair**: Termina o programa

### 3. API RESTful
- **Tecnologia**: FastAPI
- **Acesso**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Endpoints**:
  - POST /chat: Processar queries
  - GET /health: Status do sistema
  - DELETE /sessions/{id}: Limpar sessão

### Exemplos de Uso

```
Você: tem mochila amarela?
Assistente: Desculpe, não encontrei produtos que correspondam.
Você pode buscar diretamente no site: 
https://www.signa.pt/brindes/pesquisa.asp?q=mochila&idCorPrincipal=6

Você: canecas azuis
Assistente: Encontrei 2 produtos:
1. Caneca Cerâmica Azul - https://www.signa.pt/...
2. Caneca Térmica Azul - https://www.signa.pt/...

Para ver todos os produtos azuis:
https://www.signa.pt/brindes/pesquisa.asp?q=canecas&idCorPrincipal=1
```

## Base de Conhecimento

### Estrutura de Dados

```python
{
    "products": [
        {
            "id": "12345",
            "name": "Caneca Cerâmica",
            "category": "Casa & Lar",
            "colors": ["azul", "vermelho"],
            "price": 4.50,
            "url": "https://..."
        }
    ],
    "categories": {
        "1": {
            "name": "Beleza e Saúde",
            "url": "https://..."
        }
    }
}
```

### Persistência
- Formato: Python pickle
- Ficheiro: `knowledge_base.pkl`
- Carregamento automático
- Atualização via comando `crawl`

## Integração OpenAI

### Modelos Utilizados
- **Padrão**: gpt-4o-mini (rápido e económico)
- **Configurável**: Via variável OPENAI_MODEL

### Prompts Otimizados
1. **Análise de Query**: JSON estruturado
2. **Resposta Contextual**: Tom profissional
3. **Temperatura**: 0.1 para consistência

## Modo Debug

Quando `DEBUG_MODE=True`:
- Logs detalhados de cada operação
- Rastreamento de erros completo
- Tempos de resposta
- Queries SQL/pesquisa

## Performance

### Otimizações
1. **Async/Await**: Operações não-bloqueantes
2. **Caching**: Reduz chamadas à API
3. **Batch Processing**: Crawling paralelo
4. **Lazy Loading**: Carrega dados conforme necessário

### Métricas Típicas
- Resposta do chatbot: < 2 segundos
- Crawling completo: 5-10 minutos
- Pesquisa local: < 100ms

## Limitações Conhecidas

1. **Dados Mock**: Usa dados exemplo se crawling falhar
2. **Cores Limitadas**: Apenas cores principais mapeadas
3. **Contexto**: Mantém apenas últimas 5 mensagens
4. **Rate Limits**: Dependente de limites OpenAI