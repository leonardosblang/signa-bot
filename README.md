# Signa Chatbot

Chatbot inteligente para responder perguntas sobre a empresa Signa e seus produtos.

## Instalação Rápida

### Windows

Simplesmente execute:
```
run.bat
```

1. **Primeira vez**: Escolha opção 4 (Instalação limpa)
2. **Após instalação**: Escolha opção 1 (Interface Web - Recomendado)
3. **Aceda**: http://localhost:8501

### Manual

1. Criar ambiente virtual:
```bash
python -m venv venv
```

2. Ativar ambiente virtual:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

3. Instalar dependências:
```bash
pip install -r requirements.txt
```

4. Executar o chatbot:
```bash
python main.py
```

## Funcionalidades

- Pesquisa de produtos por nome, categoria, cor e preço
- Informações sobre a empresa Signa
- Base de conhecimento atualizada automaticamente
- Interface CLI interativa

## Exemplos de Uso

- "tem caneca azul?" - Procura canecas azuis
- "mochilas baratas" - Procura mochilas com preço baixo
- "bolsas verdes" - Procura bolsas verdes com link filtrado
- "produtos de tecnologia" - Mostra produtos de tecnologia

## Arquitetura

O projeto utiliza arquitetura hexagonal (ports and adapters) com:
- Domain: Modelos de negócio
- Application: Serviços de aplicação
- Infrastructure: Adaptadores (crawler, chatbot, knowledge base)
- Ports: Interfaces

## Configuração

Edite o arquivo `.env` para configurar:
- `OPENAI_API_KEY`: Chave da API OpenAI
- `OPENAI_MODEL`: Modelo a usar (padrão: gpt-4o-mini)
- `DEBUG_MODE`: Ativar logs de debug
- `CRAWL_TIMEOUT`: Timeout para crawling
- `MAX_RETRIES`: Tentativas máximas
- `CACHE_ENABLED`: Ativar cache
- `CACHE_TTL`: Tempo de vida do cache