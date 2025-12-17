#!/usr/bin/env python3
"""
CLI do OpenAgent - Interface de Linha de Comando
"""

import argparse
import sys
import os
from pathlib import Path

from .core import OpenAgent

def create_parser():
    """Cria o parser de argumentos da CLI"""
    parser = argparse.ArgumentParser(
        prog="openagent",
        description="OpenAgent - Agente de IA Local 100% Open Source",
        epilog="""
Exemplos de uso:
  openagent                          # Inicia modo interativo
  openagent --server-only            # Apenas servidor API
  openagent --port 8080              # Servidor na porta 8080
  openagent --search mistral         # Buscar modelos
  openagent --download mistral       # Baixar modelo
  openagent --models                 # Listar modelos locais
  openagent --status                 # Mostrar status
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Grupo de modos de operação
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--server-only", 
        action="store_true",
        help="Iniciar apenas o servidor API (modo servidor)"
    )
    mode_group.add_argument(
        "--interactive", "-i",
        action="store_true", 
        default=True,
        help="Iniciar modo interativo (padrão)"
    )
    
    # Grupo de operações de modelos
    model_group = parser.add_argument_group("Operações de Modelos")
    model_group.add_argument(
        "--search", "-s",
        metavar="QUERY",
        help="Buscar modelos disponíveis"
    )
    model_group.add_argument(
        "--download", "-d",
        metavar="MODEL_ID",
        help="Baixar modelo específico"
    )
    model_group.add_argument(
        "--load", "-l",
        metavar="MODEL_ID", 
        help="Carregar modelo na memória"
    )
    model_group.add_argument(
        "--models", "-m",
        action="store_true",
        help="Listar modelos locais"
    )
    
    # Grupo de configuração
    config_group = parser.add_argument_group("Configuração")
    config_group.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host do servidor (padrão: 127.0.0.1)"
    )
    config_group.add_argument(
        "--port", "-p",
        type=int,
        default=1234,
        help="Porta do servidor (padrão: 1234)"
    )
    config_group.add_argument(
        "--config",
        metavar="PATH",
        help="Caminho do diretório de configuração"
    )
    config_group.add_argument(
        "--source",
        choices=["all", "huggingface", "ollama"],
        default="all",
        help="Fonte de busca de modelos (padrão: all)"
    )
    
    # Grupo de informações
    info_group = parser.add_argument_group("Informações")
    info_group.add_argument(
        "--status",
        action="store_true",
        help="Mostrar status do sistema"
    )
    info_group.add_argument(
        "--version", "-v",
        action="version",
        version="OpenAgent 1.0.0"
    )
    info_group.add_argument(
        "--debug",
        action="store_true",
        help="Ativar modo debug"
    )
    
    return parser

def handle_model_operations(agent, args):
    """Lida com operações de modelos"""
    
    if args.search:
        print(f"🔍 Buscando modelos: {args.search}")
        models = agent.search_models_interactive(args.search, args.source)
        if not models:
            print("❌ Nenhum modelo encontrado.")
            return False
        return True
    
    if args.download:
        print(f"⬇️ Baixando modelo: {args.download}")
        success = agent.download_model_interactive(args.download)
        return success
    
    if args.load:
        print(f"🔄 Carregando modelo: {args.load}")
        success = agent.load_model_interactive(args.load)
        return success
    
    if args.models:
        agent.list_local_models()
        return True
    
    if args.status:
        agent._show_status()
        return True
    
    return None

def main():
    """Função principal da CLI"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Se nenhum argumento foi fornecido, mostra ajuda
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    try:
        # Inicializa o OpenAgent
        config_path = args.config or os.path.expanduser("~/.openagent")
        agent = OpenAgent(config_path)
        
        # Configura servidor se especificado
        if args.host != "127.0.0.1" or args.port != 1234:
            agent.llm_server.host = args.host
            agent.llm_server.port = args.port
        
        # Handle operações de modelos
        model_result = handle_model_operations(agent, args)
        if model_result is not None:
            return 0 if model_result else 1
        
        # Modo servidor apenas
        if args.server_only:
            print("🚀 Iniciando OpenAgent em modo servidor...")
            if not agent.start_server():
                print("❌ Falha ao iniciar servidor")
                return 1
            
            print(f"🖥️ Servidor rodando em http://{args.host}:{args.port}")
            print("Pressione Ctrl+C para parar...")
            
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Encerrando servidor...")
                agent.stop_server()
                return 0
        
        # Modo interativo (padrão)
        else:
            print("🚀 Iniciando OpenAgent...")
            
            if not agent.start_server():
                print("❌ Falha ao iniciar servidor")
                return 1
            
            try:
                agent.interactive_shell()
            except KeyboardInterrupt:
                print("\n👋 Até logo!")
            finally:
                agent.stop_server()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 Operação cancelada pelo usuário.")
        return 0
    except Exception as e:
        if args.debug:
            import traceback
            traceback.print_exc()
        else:
            print(f"❌ Erro: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())