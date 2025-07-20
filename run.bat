@echo off
setlocal enabledelayedexpansion

echo =====================================
echo    Signa Chatbot - Launcher v2.1
echo =====================================
echo.
echo Interface Grafica: Opcao 2 (recomendado)
echo Interface CLI: Opcao 1  
echo Instalacao completa: Opcao 4
echo.

:MENU
echo Escolha uma opcao:
echo 1. Executar chatbot (CLI)
echo 2. Executar interface web (GUI)
echo 3. Executar servidor API
echo 4. Instalacao limpa (remove e reinstala tudo)
echo 5. Atualizar base de dados (crawl)
echo 6. Instalar/Atualizar dependencias
echo 7. Criar ambiente virtual apenas
echo 8. Executar com Docker
echo 9. Parar todos os servicos
echo 10. Verificar status
echo 11. Sair
echo.

set /p choice="Digite sua escolha (1-11): "

if "%choice%"=="1" goto RUN
if "%choice%"=="2" goto RUN_WEB
if "%choice%"=="3" goto RUN_API
if "%choice%"=="4" goto CLEAN_INSTALL
if "%choice%"=="5" goto UPDATE_DATABASE
if "%choice%"=="6" goto UPDATE_DEPS
if "%choice%"=="7" goto CREATE_VENV_ONLY
if "%choice%"=="8" goto RUN_DOCKER
if "%choice%"=="9" goto STOP_SERVICES
if "%choice%"=="10" goto CHECK_STATUS
if "%choice%"=="11" goto EXIT

echo Opcao invalida! Por favor, escolha entre 1 e 11.
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

:RUN_WEB
echo.
echo [INFO] Iniciando interface web completa (API + Frontend)...

if not exist "venv" (
    echo [ERRO] Ambiente virtual nao encontrado. Execute a instalacao primeiro.
    pause
    goto MENU
)

echo [INFO] Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo [INFO] Testando componentes...
python -c "from presentation.api.main import app; print('[OK] API ready')" 2>nul || (
    echo [ERRO] Falha na validacao da API. Verifique as dependencias.
    pause
    goto MENU
)

python -c "import streamlit; print('[OK] Streamlit ready')" 2>nul || (
    echo [ERRO] Falha na validacao do Streamlit. Verifique as dependencias.
    pause
    goto MENU
)

echo [INFO] Iniciando servidor API em background...
start /B python run_api.py

echo [INFO] Aguardando API inicializar...
timeout /t 5 >nul

echo [INFO] Iniciando interface web...
echo [INFO] A interface sera aberta automaticamente em http://localhost:8501
echo [INFO] API estara disponivel em http://localhost:8000
echo.
echo IMPORTANTE: Use http://localhost:8501 (NAO 0.0.0.0:8501)
echo [INFO] Para parar, feche esta janela ou pressione Ctrl+C
echo.

python run_web.py

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao executar a interface web.
    echo [INFO] Verifique se todas as dependencias estao instaladas.
    pause
)

goto END

:RUN_API
echo.
echo [INFO] Iniciando servidor API...

if not exist "venv" (
    echo [ERRO] Ambiente virtual nao encontrado. Execute a instalacao primeiro.
    pause
    goto MENU
)

call venv\Scripts\activate.bat

echo [INFO] Iniciando FastAPI na porta 8000...
echo [INFO] API estara disponivel em http://localhost:8000
echo [INFO] Documentacao em http://localhost:8000/docs
echo [INFO] Pressione Ctrl+C para parar.
echo.

python run_api.py

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao executar o servidor API.
    echo [INFO] Verifique se todas as dependencias estao instaladas.
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

echo Escolha como executar o chatbot:
echo 1. Interface Web (recomendado)
echo 2. Interface CLI
echo 3. Servidor API apenas
echo 4. Voltar ao menu principal
echo.

set /p post_install_choice="Digite sua escolha (1-4): "

if "%post_install_choice%"=="1" goto RUN_WEB
if "%post_install_choice%"=="2" goto RUN
if "%post_install_choice%"=="3" goto RUN_API
if "%post_install_choice%"=="4" goto MENU

echo Opcao invalida! Iniciando interface web...
goto RUN_WEB

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
echo.
echo Escolha o modo Docker:
echo A. Interface Web (recomendado)
echo B. Servidor API apenas
echo C. CLI
echo D. Docker Compose (API + Web)
echo.

set /p docker_choice="Digite sua escolha (A-D): "

if /i "%docker_choice%"=="A" goto DOCKER_WEB
if /i "%docker_choice%"=="B" goto DOCKER_API
if /i "%docker_choice%"=="C" goto DOCKER_CLI
if /i "%docker_choice%"=="D" goto DOCKER_COMPOSE

echo Opcao invalida!
goto RUN_DOCKER

:DOCKER_WEB
echo [INFO] Construindo e executando interface web...
docker build -t signa-chatbot .
if errorlevel 1 goto DOCKER_ERROR
docker run -p 8501:8501 --env-file .env signa-chatbot web
goto DOCKER_END

:DOCKER_API
echo [INFO] Construindo e executando servidor API...
docker build -t signa-chatbot .
if errorlevel 1 goto DOCKER_ERROR
docker run -p 8000:8000 --env-file .env signa-chatbot api
goto DOCKER_END

:DOCKER_CLI
echo [INFO] Construindo e executando CLI...
docker build -t signa-chatbot .
if errorlevel 1 goto DOCKER_ERROR
docker run -it --env-file .env signa-chatbot cli
goto DOCKER_END

:DOCKER_COMPOSE
echo [INFO] Executando com Docker Compose...
docker-compose up --build -d
echo.
echo [INFO] Servicos iniciados:
echo - API: http://localhost:8000
echo - Web: http://localhost:8501
echo.
echo Para parar: docker-compose down
goto DOCKER_END

:DOCKER_ERROR
echo [ERRO] Falha ao construir imagem Docker.
echo [INFO] Certifique-se de que Docker esta instalado e em execucao.
goto DOCKER_END

:DOCKER_END
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