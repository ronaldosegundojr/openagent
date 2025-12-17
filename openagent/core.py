#!/usr/bin/env python3
"""
OpenAgent - Agente de IA Local 100% Open Source
Um sistema completo de agente LLM local semelhante ao Opencode, mas 100% independente.
"""

import os
import sys
import json
import argparse
import threading
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# Importar módulos locais
from .model_manager import ModelManager
from .llm_server import LLMServer
from .tools import ToolRegistry

class OpenAgent:
    """Classe principal do OpenAgent"""
    
    def __init__(self, config_path: str = "./config"):
        self.config_path = Path(config_path)
        self.config_path.mkdir(exist_ok=True)
        
        self.model_manager = ModelManager(str(self.config_path / "models"))
        self.llm_server = LLMServer()
        self.tool_registry = ToolRegistry()
        
        self.config_file = self.config_path / "openagent.json"
        self.config = self._load_config()
        
        self.running = False
        self.server_thread = None
    
    def _load_config(self) -> Dict:
        """Carrega configuração do arquivo"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
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
    
    def _save_config(self):
        """Salva configuração no arquivo"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def start_server(self) -> bool:
        """Inicia o servidor LLM"""
        try:
            self.llm_server.start()
            self.running = True
            return True
        except Exception as e:
            print(f"❌ Erro ao iniciar servidor: {e}")
            return False
    
    def stop_server(self):
        """Para o servidor LLM"""
        if self.running:
            self.llm_server.stop()
            self.running = False
    
    def search_models_interactive(self, query: str = "", source: str = "all"):
        """Busca modelos de forma interativa"""
        print(f"🔍 Buscando modelos{' em ' + source if source != 'all' else ''}...")
        
        models = self.model_manager.search_models(query, source)
        
        if not models:
            print("❌ Nenhum modelo encontrado.")
            return
        
        print(f"\n📋 Encontrados {len(models)} modelos:\n")
        
        for i, model in enumerate(models, 1):
            capabilities = model.get("capabilities", {})
            caps_str = []
            
            if capabilities.get("tools"): caps_str.append("🔧 Tools")
            if capabilities.get("reasoning"): caps_str.append("🧠 Reasoning")
            if capabilities.get("vision"): caps_str.append("👁️ Vision")
            if capabilities.get("code"): caps_str.append("💻 Code")
            if capabilities.get("chat"): caps_str.append("💬 Chat")
            if capabilities.get("multimodal"): caps_str.append("🎨 Multimodal")
            
            caps_display = " | ".join(caps_str) if caps_str else "📝 Text"
            
            print(f"{i:2d}. 📦 {model['name']}")
            print(f"     📝 {model['description'][:80]}{'...' if len(model['description']) > 80 else ''}")
            print(f"     📊 {model.get('size', 'Unknown')} | ⬇️ {model.get('downloads', 0):,} downloads | ❤️ {model.get('likes', 0):,}")
            print(f"     🏷️ {model.get('source', 'unknown').title()} | {caps_display}")
            print()
        
        return models
    
    def download_model_interactive(self, model_id: str) -> bool:
        """Baixa um modelo de forma interativa"""
        print(f"⬇️ Iniciando download do modelo: {model_id}")
        
        def progress_callback(message):
            print(f"   {message}")
        
        success = self.model_manager.download_model(model_id, progress_callback)
        
        if success:
            print(f"✅ Modelo {model_id} baixado com sucesso!")
            
            # Pergunta se quer carregar o modelo
            response = input("🔄 Deseja carregar este modelo agora? (s/N): ").strip().lower()
            if response in ['s', 'sim', 'y', 'yes']:
                return self.load_model_interactive(model_id)
        else:
            print(f"❌ Falha ao baixar modelo {model_id}")
        
        return success
    
    def load_model_interactive(self, model_id: str) -> bool:
        """Carrega um modelo de forma interativa"""
        print(f"🔄 Carregando modelo: {model_id}")
        
        success = self.model_manager.load_model(model_id)
        
        if success:
            print(f"✅ Modelo {model_id} carregado com sucesso!")
            self.config["models"]["last_loaded"] = model_id
            self._save_config()
        else:
            print(f"❌ Falha ao carregar modelo {model_id}")
        
        return success
    
    def list_local_models(self):
        """Lista modelos locais"""
        models = self.model_manager.list_local_models()
        active_model = self.model_manager.get_active_model()
        
        if not models:
            print("📭 Nenhum modelo local encontrado.")
            return
        
        print(f"\n📚 Modelos Locais ({len(models)}):\n")
        
        for i, model in enumerate(models, 1):
            status = "🟢 ATIVO" if model["id"] == active_model else "⚪ INATIVO"
            size_mb = model.get("size", 0) / (1024 * 1024)
            
            print(f"{i:2d}. {status} 📦 {model['id']}")
            print(f"     📁 {model['path']}")
            print(f"     📊 {size_mb:.1f} MB")
            print()
    
    def interactive_shell(self):
        """Inicia o shell interativo"""
        print("\n🚀 OpenAgent - Shell Interativo")
        print("=" * 50)
        print("Comandos disponíveis:")
        print("  /search [query] - Buscar modelos")
        print("  /download [model] - Baixar modelo")
        print("  /load [model] - Carregar modelo")
        print("  /models - Listar modelos locais")
        print("  /status - Mostrar status")
        print("  /help - Ajuda")
        print("  /quit - Sair")
        print("=" * 50)
        
        messages = [
            {
                "role": "system",
                "content": (
                    "Você é o OpenAgent, um assistente de IA local com acesso a ferramentas. "
                    "Você pode ajudar com tarefas como criar/editar arquivos, executar comandos, "
                    "buscar informações e processar imagens. Use as ferramentas disponíveis "
                    "sempre que apropriado."
                )
            }
        ]
        
        while True:
            try:
                user_input = input("\n🧑 Você: ").strip()
                
                if not user_input:
                    continue
                
                # Comandos do sistema
                if user_input.startswith('/'):
                    self._handle_command(user_input)
                    continue
                
                # Processa mensagem com a IA
                messages.append({"role": "user", "content": user_input})
                
                response = self._generate_response(messages)
                
                if response:
                    messages.append({"role": "assistant", "content": response})
                    print(f"\n🤖 OpenAgent: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Até logo!")
                break
            except Exception as e:
                print(f"\n❌ Erro: {e}")
    
    def _handle_command(self, command: str):
        """Lida com comandos do shell"""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == '/search':
            query = ' '.join(parts[1:]) if len(parts) > 1 else ""
            self.search_models_interactive(query)
        
        elif cmd == '/download':
            if len(parts) < 2:
                print("❌ Uso: /download <model_id>")
                return
            
            model_id = ' '.join(parts[1:])
            self.download_model_interactive(model_id)
        
        elif cmd == '/load':
            if len(parts) < 2:
                print("❌ Uso: /load <model_id>")
                return
            
            model_id = ' '.join(parts[1:])
            self.load_model_interactive(model_id)
        
        elif cmd == '/models':
            self.list_local_models()
        
        elif cmd == '/status':
            self._show_status()
        
        elif cmd == '/help':
            self._show_help()
        
        elif cmd in ['/quit', '/exit', '/q']:
            print("👋 Encerrando OpenAgent...")
            self.stop_server()
            sys.exit(0)
        
        else:
            print(f"❌ Comando desconhecido: {cmd}")
            print("Digite /help para ver os comandos disponíveis.")
    
    def _generate_response(self, messages: List[Dict]) -> Optional[str]:
        """Gera resposta usando o modelo ativo"""
        active_model = self.model_manager.get_active_model()
        
        if not active_model:
            print("⚠️ Nenhum modelo carregado. Use /load <modelo> para carregar um modelo.")
            return None
        
        try:
            # Simulação de geração (na implementação real, usaria o modelo)
            time.sleep(1)
            
            # Extrai a última mensagem do usuário
            user_msg = messages[-1]["content"] if messages else ""
            
            # Respostas simuladas baseadas em padrões
            if "criar arquivo" in user_msg.lower():
                return "Posso ajudar você a criar um arquivo. Qual o nome e conteúdo do arquivo que deseja criar?"
            elif "executar" in user_msg.lower() or "rodar" in user_msg.lower():
                return "Posso executar comandos para você. Qual comando deseja executar?"
            elif "listar" in user_msg.lower() or "mostrar" in user_msg.lower():
                return "Posso listar arquivos e diretórios. Qual caminho deseja explorar?"
            else:
                return f"Entendi sua solicitação. Como assistente OpenAgent, posso ajudar com diversas tarefas usando as ferramentas disponíveis. O que você gostaria que eu fizesse especificamente?"
        
        except Exception as e:
            print(f"❌ Erro ao gerar resposta: {e}")
            return None
    
    def _show_status(self):
        """Mostra status atual do sistema"""
        print("\n📊 Status do OpenAgent:")
        print(f"   🖥️ Servidor: {'🟢 Online' if self.running else '🔴 Offline'}")
        print(f"   📦 Modelo Ativo: {self.model_manager.get_active_model() or 'Nenhum'}")
        print(f"   📁 Diretório de Trabalho: {os.getcwd()}")
        print(f"   📚 Modelos Locais: {len(self.model_manager.list_local_models())}")
    
    def _show_help(self):
        """Mostra ajuda"""
        print("\n📖 Ajuda do OpenAgent:")
        print("\n🔧 Comandos do Sistema:")
        print("   /search [query]     - Buscar modelos disponíveis")
        print("   /download <model>   - Baixar um modelo")
        print("   /load <model>       - Carregar um modelo")
        print("   /models             - Listar modelos locais")
        print("   /status             - Mostrar status do sistema")
        print("   /help               - Mostrar esta ajuda")
        print("   /quit               - Sair do OpenAgent")
        print("\n💬 Exemplos de uso:")
        print("   Crie um arquivo Python com hello world")
        print("   Liste os arquivos no diretório atual")
        print("   Execute o comando 'python --version'")
        print("   Busque por 'mistral' para encontrar modelos")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="OpenAgent - Agente de IA Local")
    parser.add_argument("--config", default="./config", help="Diretório de configuração")
    parser.add_argument("--server-only", action="store_true", help="Iniciar apenas o servidor")
    parser.add_argument("--port", type=int, default=1234, help="Porta do servidor")
    parser.add_argument("--host", default="127.0.0.1", help="Host do servidor")
    
    args = parser.parse_args()
    
    # Inicia OpenAgent
    agent = OpenAgent(args.config)
    
    # Configura servidor se especificado
    if args.host != "127.0.0.1" or args.port != 1234:
        agent.llm_server.host = args.host
        agent.llm_server.port = args.port
    
    print("🚀 Iniciando OpenAgent...")
    
    # Inicia servidor
    if not agent.start_server():
        print("❌ Falha ao iniciar servidor")
        sys.exit(1)
    
    if args.server_only:
        print(f"🖥️ Servidor rodando em http://{args.host}:{args.port}")
        print("Pressione Ctrl+C para parar...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Encerrando servidor...")
    else:
        # Inicia shell interativo
        agent.interactive_shell()
    
    agent.stop_server()

if __name__ == "__main__":
    main()