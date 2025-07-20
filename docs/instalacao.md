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

### Windows (com Batch)
```bash
run.bat
```
Escolha opção 1 para executar

### Execução Manual
```bash
python main.py
```

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

## Docker (Opcional)

Para usar com Docker:

1. **Construir imagem**
   ```bash
   docker build -t signa-chatbot .
   ```

2. **Executar container**
   ```bash
   docker run -it --env-file .env signa-chatbot
   ```

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