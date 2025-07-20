# Arquitetura do Signa Chatbot

## Visão Geral

O Signa Chatbot utiliza uma arquitetura hexagonal (Ports and Adapters), que promove a separação de responsabilidades e facilita a manutenção e testabilidade do código.

## Estrutura de Pastas

```
signa-chatbot/
├── domain/              # Modelos de negócio
├── application/         # Serviços de aplicação
├── infrastructure/      # Adaptadores e implementações
│   ├── adapters/       # Implementações concretas
│   ├── config/         # Configurações
│   └── utils/          # Utilitários
├── ports/              # Interfaces (contratos)
├── docs/               # Documentação
└── main.py            # Ponto de entrada
```

## Camadas da Arquitetura

### 1. Domain (Domínio)
Contém os modelos de negócio essenciais:
- `Product`: Representa um produto com nome, categoria, cores, preço e URL
- `CategoryInfo`: Informações sobre categorias de produtos
- `SearchQuery`: Consulta de pesquisa com filtros
- `SearchResult`: Resultado de uma pesquisa
- `ChatMessage`: Mensagem de chat

### 2. Application (Aplicação)
Serviços que orquestram a lógica de negócio:
- `ChatbotService`: Gerencia conversas e histórico
- `CrawlerService`: Coordena o processo de web scraping

### 3. Infrastructure (Infraestrutura)
Implementações concretas dos adaptadores:

#### Adapters
- `OpenAIChatbotAdapter`: Integração com OpenAI para processamento de linguagem natural
- `InMemoryKnowledgeBase`: Armazenamento persistente em pickle
- `SimpleCrawlerAdapter`: Web scraping usando BeautifulSoup

#### Config
- Gestão de configurações via variáveis de ambiente (.env)
- Validação de configurações obrigatórias

### 4. Ports (Portas)
Interfaces que definem contratos:
- `ChatbotPort`: Interface para chatbot
- `KnowledgeBasePort`: Interface para base de conhecimento
- `CrawlerPort`: Interface para web scraping

## Fluxo de Dados

1. **Entrada do Utilizador** → CLI (main.py)
2. **Processamento** → ChatbotService
3. **Análise de Intenção** → OpenAIChatbotAdapter
4. **Pesquisa de Produtos** → KnowledgeBase
5. **Geração de Resposta** → OpenAI + Filtros
6. **Saída** → CLI com links filtrados

## Padrões Utilizados

### Hexagonal Architecture
- Separação clara entre lógica de negócio e detalhes técnicos
- Facilita testes e mudanças de implementação
- Ports definem contratos, Adapters implementam

### Dependency Injection
- Serviços recebem dependências no construtor
- Facilita testes com mocks
- Reduz acoplamento

### Repository Pattern
- KnowledgeBase abstrai o armazenamento
- Permite trocar entre diferentes implementações

## Componentes Principais

### ChatbotAdapter
- Analisa queries usando OpenAI
- Extrai intenções e parâmetros (produto, cor, preço)
- Gera URLs com filtros de cor

### KnowledgeBase
- Armazena produtos e categorias
- Suporta pesquisa com filtros
- Persistência em arquivo pickle

### CrawlerAdapter
- Extrai dados do site Signa
- Processa HTML e extrai produtos
- Fallback para dados mock em caso de erro

## Considerações de Design

1. **Modularidade**: Cada componente tem responsabilidade única
2. **Extensibilidade**: Fácil adicionar novos adaptadores
3. **Testabilidade**: Interfaces permitem uso de mocks
4. **Resiliência**: Fallbacks para garantir funcionamento