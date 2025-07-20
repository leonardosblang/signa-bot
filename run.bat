@echo off
setlocal enabledelayedexpansion

echo =====================================
echo    Signa Chatbot - Launcher v2.0
echo =====================================
echo.

:MENU
echo Escolha uma opcao:
echo 1. Executar chatbot
echo 2. Instalacao limpa (remove e reinstala tudo)
echo 3. Atualizar base de dados (crawl)
echo 4. Instalar/Atualizar dependencias
echo 5. Criar ambiente virtual apenas
echo 6. Executar com Docker
echo 7. Parar todos os servicos
echo 8. Verificar status
echo 9. Sair
echo.

set /p choice="Digite sua escolha (1-9): "

if "%choice%"=="1" goto RUN
if "%choice%"=="2" goto CLEAN_INSTALL
if "%choice%"=="3" goto UPDATE_DATABASE
if "%choice%"=="4" goto UPDATE_DEPS
if "%choice%"=="5" goto CREATE_VENV_ONLY
if "%choice%"=="6" goto RUN_DOCKER
if "%choice%"=="7" goto STOP_SERVICES
if "%choice%"=="8" goto CHECK_STATUS
if "%choice%"=="9" goto EXIT

echo Opcao invalida! Por favor, escolha entre 1 e 9.
echo.
goto MENU

:RUN
echo.
echo [INFO] Verificando ambiente virtual...

if not exist "venv" (
    echo [AVISO] Ambiente virtual nao encontrado. Criando...
    goto CREATE_VENV
)

echo [INFO] Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo [INFO] Iniciando Signa Chatbot...
python main.py

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao executar o chatbot.
    echo [INFO] Tente a instalacao limpa (opcao 2).
    pause
)

goto END

:CLEAN_INSTALL
echo.
echo [AVISO] Isto ira remover:
echo - Ambiente virtual (venv)
echo - Cache do crawler
echo - Base de conhecimento local
echo.

set /p confirm="Tem certeza? (S/N): "
if /i not "%confirm%"=="S" goto MENU

echo.
echo [INFO] Removendo arquivos antigos...

if exist "venv" (
    echo [INFO] Removendo ambiente virtual...
    rmdir /s /q venv
)

if exist "knowledge_base.pkl" (
    echo [INFO] Removendo base de conhecimento...
    del /q knowledge_base.pkl
)

if exist "__pycache__" (
    echo [INFO] Removendo cache Python...
    for /d %%i in (*__pycache__) do rmdir /s /q "%%i"
)

:CREATE_VENV
echo.
echo [INFO] Criando novo ambiente virtual...
python -m venv venv

if errorlevel 1 (
    echo [ERRO] Falha ao criar ambiente virtual.
    echo [INFO] Certifique-se de que Python esta instalado.
    pause
    goto EXIT
)

echo [INFO] Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo [INFO] Atualizando pip...
python -m pip install --upgrade pip

echo [INFO] Instalando dependencias do requirements.txt...
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo [ERRO] requirements.txt nao encontrado!
    pause
    goto EXIT
)

echo.
echo [SUCESSO] Instalacao concluida!
echo.

set /p run_now="Deseja executar o chatbot agora? (S/N): "
if /i "%run_now%"=="S" goto RUN

goto END

:UPDATE_DATABASE
echo.
echo [INFO] Atualizando base de dados...

if not exist "venv" (
    echo [ERRO] Ambiente virtual nao encontrado. Execute a instalacao primeiro.
    pause
    goto MENU
)

call venv\Scripts\activate.bat

echo [INFO] Executando crawl do site Signa...
python -c "import asyncio; from main import SignaChatbotCLI; cli = SignaChatbotCLI(); asyncio.run(cli.crawl_site())"

echo.
echo [INFO] Base de dados atualizada!
pause
goto MENU

:UPDATE_DEPS
echo.
echo [INFO] Atualizando dependencias...

if not exist "venv" (
    echo [ERRO] Ambiente virtual nao encontrado. Execute a instalacao primeiro.
    pause
    goto MENU
)

call venv\Scripts\activate.bat

echo [INFO] Atualizando pip...
python -m pip install --upgrade pip

echo [INFO] Atualizando dependencias...
pip install --upgrade -r requirements.txt

echo.
echo [SUCESSO] Dependencias atualizadas!
pause
goto MENU

:CREATE_VENV_ONLY
echo.
echo [INFO] Criando ambiente virtual...

if exist "venv" (
    echo [AVISO] Ambiente virtual ja existe.
    set /p overwrite="Deseja substituir? (S/N): "
    if /i "!overwrite!"=="S" (
        rmdir /s /q venv
    ) else (
        goto MENU
    )
)

python -m venv venv

if errorlevel 1 (
    echo [ERRO] Falha ao criar ambiente virtual.
    pause
) else (
    echo [SUCESSO] Ambiente virtual criado!
    echo [INFO] Use 'venv\Scripts\activate' para ativar
)

pause
goto MENU

:RUN_DOCKER
echo.
echo [INFO] Executando com Docker...

if not exist "Dockerfile" (
    echo [ERRO] Dockerfile nao encontrado!
    echo [INFO] Criando Dockerfile basico...
    
    (
    echo FROM python:3.9-slim
    echo.
    echo WORKDIR /app
    echo.
    echo COPY requirements.txt .
    echo RUN pip install --no-cache-dir -r requirements.txt
    echo.
    echo COPY . .
    echo.
    echo CMD ["python", "main.py"]
    ) > Dockerfile
)

echo [INFO] Construindo imagem Docker...
docker build -t signa-chatbot .

if errorlevel 1 (
    echo [ERRO] Falha ao construir imagem Docker.
    echo [INFO] Certifique-se de que Docker esta instalado e em execucao.
    pause
    goto MENU
)

echo [INFO] Executando container...
docker run -it --rm --env-file .env signa-chatbot

pause
goto MENU

:STOP_SERVICES
echo.
echo [INFO] Parando servicos...
echo.

tasklist | findstr /i "python.exe" >nul
if %errorlevel%==0 (
    echo [INFO] Processos Python encontrados:
    tasklist | findstr /i "python.exe"
    echo.
    set /p kill_all="Deseja terminar todos os processos Python? (S/N): "
    if /i "!kill_all!"=="S" (
        taskkill /F /IM python.exe
        echo [INFO] Processos Python terminados.
    )
) else (
    echo [INFO] Nenhum processo Python em execucao.
)

docker ps | findstr /i "signa-chatbot" >nul
if %errorlevel%==0 (
    echo.
    echo [INFO] Container Docker encontrado.
    set /p kill_docker="Deseja parar o container? (S/N): "
    if /i "!kill_docker!"=="S" (
        docker stop signa-chatbot
        echo [INFO] Container Docker parado.
    )
)

echo.
pause
goto MENU

:CHECK_STATUS
echo.
echo [INFO] Verificando status do sistema...
echo.

echo Python:
python --version 2>nul
if errorlevel 1 (
    echo   [ERRO] Python nao instalado ou nao no PATH
) else (
    echo   [OK] Python instalado
)

echo.
echo Ambiente Virtual:
if exist "venv" (
    echo   [OK] Ambiente virtual existe
) else (
    echo   [AVISO] Ambiente virtual nao encontrado
)

echo.
echo Base de Conhecimento:
if exist "knowledge_base.pkl" (
    echo   [OK] Base de dados existe
    for %%A in (knowledge_base.pkl) do echo   Tamanho: %%~zA bytes
) else (
    echo   [AVISO] Base de dados nao encontrada
)

echo.
echo Arquivo .env:
if exist ".env" (
    echo   [OK] Arquivo de configuracao existe
) else (
    echo   [ERRO] Arquivo .env nao encontrado!
)

echo.
echo Docker:
docker --version 2>nul
if errorlevel 1 (
    echo   [INFO] Docker nao instalado ou nao no PATH
) else (
    echo   [OK] Docker instalado
)

echo.
pause
goto MENU

:END
echo.
echo [INFO] Operacao concluida.
pause
goto MENU

:EXIT
echo.
echo Obrigado por usar Signa Chatbot!
timeout /t 2 >nul
exit /b 0