@echo off
chcp 65001 > nul
title Publicar Plataforma de Arboviroses - Itaporã/MS

echo ===============================================================================
echo   PLATAFORMA DE INTELIGÊNCIA EPIDEMIOLÓGICA DE ARBOVIROSES - ITAPORÃ / MS
echo   ASSISTENTE DE PUBLICAÇÃO ONLINE E CONTROLE DE VERSÃO
echo ===============================================================================
echo.

where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [AVISO] Git não está instalado ou não foi encontrado no PATH do Windows.
    echo Baixe e instale o Git em: https://git-scm.com/
    pause
    exit /b 1
)

if not exist ".git" (
    echo [1/3] Inicializando repositório Git local...
    git init
    git branch -M main
)

echo [2/3] Adicionando arquivos ao versionamento (respeitando .gitignore)...
git add .

echo [3/3] Criando commit da versão com suporte Mobile e Publicação Online...
git commit -m "feat: suporte mobile responsivo, 7 abas analiticas, conta-ovos fiocruz e config deploy online"

echo.
echo ===============================================================================
echo   OPÇÕES DE PUBLICAÇÃO ONLINE GRATUITA:
echo ===============================================================================
echo.
echo  Opção 1: Streamlit Community Cloud (Mais Recomendado para Streamlit)
echo    - Crie um repositório no seu GitHub (ex: painel-arboviroses-itapora)
echo    - Conecte o repositório remoto:
echo        git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
echo        git push -u origin main
echo    - Acesse https://share.streamlit.io, clique em "New app" e selecione "app.py".
echo.
echo  Opção 2: Render.com (Compatibilidade total com WebSockets e render.yaml)
echo    - Acesse https://dashboard.render.com
echo    - Clique em "New +" e escolha "Blueprint", apontando para seu repositório GitHub.
echo.
echo  Opção 3: Vercel
echo    - Instale a Vercel CLI: npm i -g vercel
echo    - Execute no terminal: vercel --prod
echo.
echo ===============================================================================
pause
