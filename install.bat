@echo off
REM Script de instalação rápida do OpenAgent para Windows

echo 🚀 Instalando OpenAgent...

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado. Por favor, instale Python 3.8+ primeiro.
    echo Visite: https://python.org/downloads/
    pause
    exit /b 1
)

REM Verificar pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip não encontrado. Por favor, instale pip primeiro.
    pause
    exit /b 1
)

REM Instalar OpenAgent
echo 📦 Instalando via pip...
pip install openagent

REM Verificar instalação
openagent --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ OpenAgent instalado com sucesso!
    echo.
    echo 🎮 Para começar:
    echo    openagent --help
    echo    openagent
    echo.
    echo 📖 Documentação: https://github.com/openagent-ai/openagent
) else (
    echo ❌ Falha na instalação. Tente:
    echo    pip install --user openagent
    echo    ou
    echo    python -m pip install openagent
)

pause