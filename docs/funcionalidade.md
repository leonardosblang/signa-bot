# Funcionalidade do Signa Chatbot

## Visão Geral

O Signa Chatbot é um assistente virtual inteligente que ajuda utilizadores a encontrar produtos no catálogo da Signa, com capacidade de filtrar por cor, categoria e preço.

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

### Como Funciona o Crawler

1. **Descoberta de Categorias**
   ```
   signaplay.pt → Lista categorias → URLs de cada categoria
   ```

2. **Extração de Produtos**
   - Navega por cada categoria
   - Extrai: nome, preço, cores, URL
   - Processa paginação

3. **Processamento de Dados**
   ```python
   HTML → BeautifulSoup → Produto → KnowledgeBase
   ```

### Estratégias de Resiliência

#### Retry Logic
- 3 tentativas com backoff exponencial
- Timeout de 30 segundos por requisição
- Fallback para dados mock

#### Cache
- Armazenamento em `knowledge_base.pkl`
- TTL configurável (padrão: 1 hora)
- Carregamento automático ao iniciar

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

## Interface CLI

### Comandos Disponíveis

- **ajuda**: Mostra comandos e exemplos
- **stats**: Estatísticas da base de dados
- **crawl**: Atualiza dados do site
- **limpar**: Limpa histórico de conversa
- **sair**: Termina o programa

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