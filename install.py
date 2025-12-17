#!/usr/bin/env python3
"""
Script de instalação do OpenAgent
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 8):
        print("❌ OpenAgent requer Python 3.8 ou superior")
        print(f"   Versão atual: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detectado")

def install_dependencies():
    """Instala as dependências necessárias"""
    print("📦 Instalando dependências...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        sys.exit(1)

def create_directories():
    """Cria diretórios necessários"""
    directories = ["config", "config/models", "config/logs"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Diretório criado: {directory}")

def create_config():
    """Cria arquivo de configuração padrão"""
    config_path = "config/openagent.json"
    
    if not os.path.exists(config_path):
        config = {
            "server": {
                "host": "127.0.0.1",
                "port": 1234
            },
            "ui": {
                "theme": "dark",
                "show_models_info": True
            },
            "models": {
                "auto_load_last": True,
                "preferred_source": "all"
            }
        }
        
        import json
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"⚙️ Configuração criada: {config_path}")

def check_system():
    """Verifica informações do sistema"""
    print(f"🖥️ Sistema: {platform.system()} {platform.release()}")
    print(f"🏗️ Arquitetura: {platform.machine()}")
    
    # Verifica se há GPU (básico)
    try:
        if platform.system() == "Windows":
            result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
            if result.returncode == 0:
                print("🎮 GPU NVIDIA detectada")
            else:
                print("⚠️ Nenhuma GPU NVIDIA detectada (usando CPU)")
        else:
            print("⚠️ Detecção de GPU disponível apenas em Windows")
    except:
        print("⚠️ Não foi possível detectar GPU")

def main():
    """Função principal de instalação"""
    print("🚀 Instalador OpenAgent")
    print("=" * 40)
    
    check_python_version()
    check_system()
    install_dependencies()
    create_directories()
    create_config()
    
    print("\n✅ Instalação concluída com sucesso!")
    print("\n🎮 Para iniciar o OpenAgent:")
    print("   python openagent.py")
    print("\n📖 Para mais informações:")
    print("   cat README.md")
    print("\n🔧 Para modo servidor:")
    print("   python openagent.py --server-only")

if __name__ == "__main__":
    main()