#!/bin/bash
# Script de instalação rápida do OpenAgent

set -e

echo "🚀 Instalando OpenAgent..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.8+ primeiro."
    exit 1
fi

# Verificar pip
if ! command -v pip &> /dev/null; then
    echo "❌ pip não encontrado. Por favor, instale pip primeiro."
    exit 1
fi

# Instalar OpenAgent
echo "📦 Instalando via pip..."
pip install openagent

# Verificar instalação
if command -v openagent &> /dev/null; then
    echo "✅ OpenAgent instalado com sucesso!"
    echo ""
    echo "🎮 Para começar:"
    echo "   openagent --help"
    echo "   openagent"
    echo ""
    echo "📖 Documentação: https://github.com/openagent-ai/openagent"
else
    echo "❌ Falha na instalação. Tente:"
    echo "   pip install --user openagent"
    echo "   ou"
    echo "   python3 -m pip install openagent"
fi