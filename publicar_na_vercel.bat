@echo off
chcp 65001 > nul
title Publicar na Vercel - Plataforma de Arboviroses Itaporã/MS

echo ===============================================================================
echo   PUBLICAR NA VERCEL - PLATAFORMA DE ARBOVIROSES ITAPORÃ / MS
echo ===============================================================================
echo.

echo [1/2] Verificando ambiente Vercel...
where vercel >nul 2>nul
if %errorlevel% equ 0 (
    echo [2/2] Publicando em produção com a Vercel CLI...
    vercel --prod
) else (
    echo [2/2] Executando publicação via npx vercel --prod...
    npx vercel --prod
)

echo.
echo ===============================================================================
echo   Processo concluído!
echo ===============================================================================
pause
