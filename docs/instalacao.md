# Instalação do Signa Chatbot

## Requisitos

- Python 3.8 ou superior
- Windows, Linux ou macOS
- Conexão à internet
- Chave API da OpenAI

## Instalação Rápida (Windows)

### Método 1: Usando o Batch File

1. Execute o ficheiro `run.bat`
2. Escolha a opção **2** (Instalação limpa) na primeira execução
3. O script irá:
   - Criar ambiente virtual
   - Instalar todas as dependências
   - Configurar o projeto

### Método 2: Instalação Manual

1. **Criar ambiente virtual**
   ```bash
   python -m venv venv
   ```

2. **Ativar ambiente virtual**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

3. **Instalar dependências**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configurar crawl4ai** (após instalar requirements.txt)
   ```bash
   crawl4ai-setup
   ```

## Configuração

### 1. Configurar Variáveis de Ambiente

Crie ou edite o ficheiro `.env` na raiz do projeto:

```env
# Configuração OpenAI (OBRIGATÓRIO)
OPENAI_API_KEY=sua_chave_api_aqui
OPENAI_MODEL=gpt-4o-mini

# Configurações de Debug
DEBUG_MODE=True

# Configurações de Crawling
CRAWL_TIMEOUT=30
MAX_RETRIES=3

# Configurações de Cache
CACHE_ENABLED=True
CACHE_TTL=3600
```

### 2. Obter Chave API OpenAI

1. Aceda a [platform.openai.com](https://platform.openai.com)
2. Crie uma conta ou faça login
3. Vá para API Keys
4. Crie uma nova chave
5. Copie e cole no `.env`

## Executar o Chatbot

### Opções Disponíveis

#### 1. Interface Gráfica (Recomendado)
```bash
run.bat
```
Escolha opção 2 (Interface Web)

Ou execute diretamente:
```bash
python run_web.py
```
Aceda a http://localhost:8501

#### 2. Interface de Linha de Comando (CLI)
```bash
run.bat
```
Escolha opção 1 (CLI)

Ou execute diretamente:
```bash
python main.py
```

#### 3. Servidor API
```bash
run.bat
```
Escolha opção 3 (Servidor API)

Ou execute diretamente:
```bash
python run_api.py
```
API disponível em http://localhost:8000
Documentação em http://localhost:8000/docs

## Estrutura de Ficheiros Criados

Após a primeira execução:
- `venv/` - Ambiente virtual Python
- `knowledge_base.pkl` - Base de dados local
- `__pycache__/` - Cache Python

## Resolução de Problemas

### Erro: "Python não encontrado"
- Instale Python 3.8+ de [python.org](https://python.org)
- Adicione Python ao PATH do sistema

### Erro: "Chave API inválida"
- Verifique se a chave no `.env` está correta
- Confirme se tem créditos na conta OpenAI

### Erro durante crawling
- O sistema usa dados mock como fallback
- Verifique conexão à internet
- Tente comando `crawl` no chatbot

### Ambiente virtual não ativa
- Windows: Execute como Administrador
- Verifique política de execução PowerShell:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

## Docker - Multi-Interface

O Signa Chatbot oferece três interfaces diferentes via Docker com suporte completo para crawl4ai.

### 1. Construir a Imagem
```bash
docker build -t signa-chatbot .
```

### 2. Opções de Execução

#### Interface CLI (Interativa)
```bash
# Execução simples
docker run -it --env-file .env signa-chatbot cli

# Com docker-compose
docker-compose --profile cli up signa-cli
```

#### API REST (FastAPI)
```bash
# Execução simples
docker run -p 8000:8000 --env-file .env signa-chatbot api

# Com docker-compose (recomendado)
docker-compose up signa-api
```
Acesso: http://localhost:8000  
Documentação: http://localhost:8000/docs

#### Interface Web (Streamlit)
```bash
# Execução simples
docker run -p 8501:8501 --env-file .env signa-chatbot web

# Com docker-compose (recomendado)
docker-compose up signa-web
```
Acesso: http://localhost:8501

#### Todos os Serviços
```bash
# API + Web Interface
docker-compose up

# Incluir CLI interativo
docker-compose --profile cli up
```

### 3. Comandos Docker-Compose Úteis

```bash
# Verificar instalação crawl4ai
docker-compose --profile setup up signa-setup

# Ver logs de um serviço
docker-compose logs signa-api

# Reconstruir após mudanças
docker-compose up --build

# Parar todos os serviços
docker-compose down

# Limpar volumes (remove base de dados)
docker-compose down -v
```

### 4. Variáveis de Ambiente Docker

Crie ficheiro `.env` para Docker:
```env
# OpenAI (obrigatório)
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-4o-mini

# Configurações gerais
DEBUG_MODE=False
CRAWL_TIMEOUT=30
MAX_RETRIES=3
CACHE_ENABLED=True
CACHE_TTL=3600

# Configurações específicas crawl4ai
CRAWL4AI_BROWSER_TYPE=chromium
```

### 5. Volumes Persistentes

- `signa_knowledge`: Base de conhecimento partilhada
- `signa_logs`: Logs dos serviços
- `./knowledge_base.pkl`: Ficheiro local sincronizado

### 6. Health Checks e Monitorização

```bash
# Verificar estado dos serviços
docker-compose ps

# Ver health status
docker inspect signa-chatbot-api | grep Health

# Logs em tempo real
docker-compose logs -f signa-api
```

## Início Rápido

Para começar a usar imediatamente:

1. **Execute o instalador**:
   ```bash
   run.bat
   ```

2. **Escolha opção 4** (Instalação limpa)

3. **Após instalação, escolha opção 1** (Interface Web)

4. **Aceda http://localhost:8501** no navegador

## Atualização

Para atualizar o chatbot:

1. Via `run.bat`: Escolha opção 2 (Instalação limpa)
2. Manual:
   ```bash
   git pull
   pip install -r requirements.txt --upgrade
   ```

## Desinstalação

1. Remova a pasta do projeto
2. Opcional: Remova Python e dependências globais