#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAgent - Core Engine
Gerencia o servidor, modelos e o loop de execução do agente com configurações avançadas.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from openai import OpenAI

# Importar módulos locais
from .model_manager import ModelManager
from .llm_server import LLMServer
from .tools import ToolRegistry
from .ui import ui

PREDEFINED_PROMPTS = {
    "Hacker": "Você é um agente hacker de elite. Responda de forma técnica, direta e use ferramentas de terminal para tudo.",
    "Assistente": "Você é um assistente prestativo e educado, focado em ajudar o usuário com tarefas do dia a dia.",
    "Analista": "Você é um analista de dados e arquivos. Sua especialidade é ler documentos e extrair informações precisas.",
    "Programador": "Você é um especialista em desenvolvimento de software. Foque em criar, editar e revisar códigos."
}

class OpenAgent:
    """Classe principal do OpenAgent"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.expanduser("~/.openagent")
            
        self.config_path = Path(config_path)
        self.config_path.mkdir(exist_ok=True, parents=True)
        
        self.config_file = self.config_path / "openagent.json"
        self.config = self._load_config()
        
        # Inicializa componentes com a config carregada
        self.model_manager = ModelManager(str(self.config_path / "models"))
        self.llm_server = LLMServer()
        self.llm_server.model_manager = self.model_manager
        self.tool_registry = ToolRegistry()
        
        self.running = False
        self.client = None
    
    def _load_config(self) -> Dict:
        """Carrega configuração do arquivo com valores padrão"""
        defaults = {
            "server": {
                "host": "127.0.0.1",
                "port": 1234,
                "enable_cors": True
            },
            "model_settings": {
                "context_length": 4096,
                "gpu_layers": -1,
                "threads": 4,
                "keep_alive": True,
                "temperature": 0.7
            },
            "agent": {
                "prompt_theme": "Hacker",
                "system_prompt": PREDEFINED_PROMPTS["Hacker"],
                "model": None,
                "mcp_enabled": True
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge recursivo simples
                    for k, v in user_config.items():
                        if isinstance(v, dict) and k in defaults:
                            defaults[k].update(v)
                        else:
                            defaults[k] = v
            except Exception as e:
                print(f"Erro ao carregar config: {e}. Usando padrões.")
        
        return defaults
    
    def _save_config(self):
        """Salva configuração no arquivo"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def start_server(self) -> bool:
        """Inicia o servidor LLM local"""
        host = self.config['server']['host']
        port = self.config['server']['port']
        ui.info(f"Iniciando servidor local em {host}:{port}...")
        
        try:
            self.llm_server.host = host
            self.llm_server.port = port
            self.llm_server.enable_cors = self.config['server']['enable_cors']
            self.llm_server.start()
            
            self.client = OpenAI(
                base_url=f"http://{host}:{port}/v1",
                api_key="local-token"
            )
            
            self.running = True
            return True
        except Exception as e:
            ui.error(f"Erro ao iniciar servidor: {e}")
            return False
    
    def stop_server(self):
        """Para o servidor LLM"""
        if self.running:
            ui.info("Encerrando servidor...")
            self.llm_server.stop()
            self.running = False
    
    def chat_loop(self, user_input: str, messages: List[Dict]):
        """Loop de pensamento e ação do agente"""
        messages.append({"role": "user", "content": user_input})
        
        max_iterations = 8
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            with ui.progress_spinner("IA Trabalhando"):
                try:
                    response = self.client.chat.completions.create(
                        model=self.config["agent"]["model"] or "local",
                        messages=messages,
                        tools=self.tool_registry.get_tool_definitions(),
                        tool_choice="auto",
                        temperature=self.config["model_settings"]["temperature"]
                    )
                except Exception as e:
                    ui.error(f"Erro na geração: {e}")
                    break

            msg = response.choices[0].message
            
            if msg.content:
                ui.print_ai_message(msg.content)
            
            if msg.tool_calls:
                messages.append(msg)
                
                for tool_call in msg.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    ui.hacker(f"Executando: [command]{tool_name}[/command]")
                    
                    # Simulação de MCP per-request context (pode ser injetado aqui)
                    if self.config["agent"]["mcp_enabled"]:
                        tool_args["_context"] = "mcp_enabled_request"

                    result = self.tool_registry.execute_tool(tool_name, tool_args)
                    result_str = json.dumps(result, indent=2) if isinstance(result, (dict, list)) else str(result)
                    
                    ui.success("Concluído.")
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": result_str
                    })
                continue
            else:
                break
        
        return messages[-1]["content"] if messages[-1]["role"] == "assistant" else ""

    def interactive_shell(self):
        """Inicia o shell interativo estilizado"""
        ui.print_banner()
        
        active_model = self.model_manager.get_active_model()
        ui.show_status({
            "Servidor": "🟢 Online",
            "Host": f"{self.llm_server.host}:{self.llm_server.port}",
            "Modelo": active_model or "⚠️ Nenhum",
            "Prompt": self.config["agent"]["prompt_theme"],
            "GPU Offload": self.config["model_settings"]["gpu_layers"]
        })
        
        messages = [
            {"role": "system", "content": self.config["agent"]["system_prompt"]}
        ]
        
        while True:
            try:
                user_msg = ui.print_user_input_prompt()
                if not user_msg: continue
                
                if user_msg.startswith('/'):
                    if self._handle_command(user_msg): break
                    continue
                
                if not active_model:
                    ui.warning("Carregue um modelo com [command]/load <id>[/command]")
                    continue
                
                self.chat_loop(user_msg, messages)
                
            except KeyboardInterrupt:
                ui.warning("\nUse /quit para sair.")

    def _handle_command(self, cmd_input: str) -> bool:
        parts = cmd_input.split()
        cmd = parts[0].lower()
        
        if cmd in ['/quit', '/exit', '/q']:
            return True
        
        elif cmd == '/help':
            ui.print_menu({
                "/models": "Lista modelos locais",
                "/search <q>": "Busca novos modelos",
                "/download <id>": "Baixa modelo",
                "/load <id>": "Carrega modelo",
                "/config": "Ver/Alterar configurações",
                "/prompt": "Mudar tema do prompt",
                "/status": "Status do sistema",
                "/quit": "Sair"
            })
            
        elif cmd == '/config':
            self._handle_config_command(parts[1:] if len(parts) > 1 else [])
            
        elif cmd == '/prompt':
            self._handle_prompt_command(parts[1:] if len(parts) > 1 else [])

        elif cmd == '/models':
            self.list_local_models()
            
        elif cmd == '/search':
            if len(parts) > 1: self.search_models_interactive(' '.join(parts[1:]))
            else: ui.error("Uso: /search <query>")

        elif cmd == '/download':
            if len(parts) > 1: self.download_model_interactive(parts[1])
            else: ui.error("Uso: /download <id>")

        elif cmd == '/load':
            if len(parts) > 1: self.load_model_interactive(parts[1])
            else: ui.error("Uso: /load <id>")
            
        elif cmd == '/status':
            self._show_status()
            
        return False

    def _handle_config_command(self, args: List[str]):
        if not args:
            ui.console.print("\n[bold cyan]Configurações Atuais:[/bold cyan]")
            ui.show_status({
                "Host": self.config["server"]["host"],
                "Porta": self.config["server"]["port"],
                "CORS": self.config["server"]["enable_cors"],
                "Contexto": self.config["model_settings"]["context_length"],
                "GPU Layers": self.config["model_settings"]["gpu_layers"],
                "Threads CPU": self.config["model_settings"]["threads"],
                "Temperatura": self.config["model_settings"]["temperature"],
                "MCP Enabled": self.config["agent"]["mcp_enabled"]
            })
            ui.info("Para alterar: /config <chave> <valor> (ex: /config threads 8)")
            return

        key, value = args[0], args[1] if len(args) > 1 else None
        if not value:
            ui.error("Forneça um valor.")
            return

        # Mapeamento de chaves amigáveis para a estrutura interna
        if key == "host": self.config["server"]["host"] = value
        elif key == "port": self.config["server"]["port"] = int(value)
        elif key == "cors": self.config["server"]["enable_cors"] = value.lower() == "true"
        elif key == "context": self.config["model_settings"]["context_length"] = int(value)
        elif key == "gpu": self.config["model_settings"]["gpu_layers"] = int(value)
        elif key == "threads": self.config["model_settings"]["threads"] = int(value)
        elif key == "temp": self.config["model_settings"]["temperature"] = float(value)
        elif key == "mcp": self.config["agent"]["mcp_enabled"] = value.lower() == "true"
        else:
            ui.error(f"Chave desconhecida: {key}")
            return

        self._save_config()
        ui.success(f"Configuração '{key}' atualizada para '{value}'.")
        ui.warning("Algumas mudanças podem exigir reinício (/quit e abrir novamente).")

    def _handle_prompt_command(self, args: List[str]):
        if not args:
            ui.info(f"Temas disponíveis: {', '.join(PREDEFINED_PROMPTS.keys())}")
            ui.info(f"Tema atual: {self.config['agent']['prompt_theme']}")
            return
        
        theme = args[0].title()
        if theme in PREDEFINED_PROMPTS:
            self.config["agent"]["prompt_theme"] = theme
            self.config["agent"]["system_prompt"] = PREDEFINED_PROMPTS[theme]
            self._save_config()
            ui.success(f"Tema alterado para {theme}. O agente agora agirá como {theme}.")
        else:
            ui.error("Tema não encontrado.")

    def list_local_models(self):
        models = self.model_manager.list_local_models()
        if not models:
            ui.warning("Nenhum modelo local.")
            return
        
        from rich.table import Table
        table = Table(title="Modelos Disponíveis")
        table.add_column("ID", style="cyan")
        table.add_column("Status", style="bold")
        
        active = self.model_manager.get_active_model()
        for m in models:
            status = "[success]ATIVO[/success]" if m['id'] == active else "[dim]Inativo[/dim]"
            table.add_row(m['id'], status)
        ui.console.print(table)

    def load_model_interactive(self, model_id: str):
        # Passa as configurações de hardware para o manager
        settings = self.config["model_settings"]
        with ui.progress_spinner(f"Carregando {model_id}"):
            success = self.model_manager.load_model(
                model_id, 
                n_ctx=settings["context_length"],
                n_threads=settings["threads"],
                n_gpu_layers=settings["gpu_layers"]
            )
        
        if success:
            ui.success(f"Modelo {model_id} pronto.")
            self.config["agent"]["model"] = model_id
            self._save_config()
        else:
            ui.error(f"Erro ao carregar {model_id}.")

    def search_models_interactive(self, query: str):
        with ui.progress_spinner(f"Buscando '{query}'"):
            models = self.model_manager.search_models(query)
        
        if not models:
            ui.warning("Vazio.")
            return

        from rich.table import Table
        table = Table(title=f"Busca: {query}")
        table.add_column("ID", style="cyan")
        table.add_column("Downs", style="green")
        for m in models:
            table.add_row(m['id'], f"{m['downloads']:,}")
        ui.console.print(table)

    def download_model_interactive(self, model_id: str):
        def cb(msg): ui.info(msg)
        if self.model_manager.download_model(model_id, progress_callback=cb):
            ui.success("Download Concluído.")
        else:
            ui.error("Erro no download.")

    def _show_status(self):
        ui.show_status({
            "Servidor": "🟢 Online" if self.running else "🔴 Offline",
            "Modelo": self.model_manager.get_active_model() or "Nenhum",
            "Contexto": self.config["model_settings"]["context_length"],
            "Cwd": os.getcwd()
        })

def main():
    agent = OpenAgent()
    if agent.start_server():
        try:
            agent.interactive_shell()
        finally:
            agent.stop_server()

if __name__ == "__main__":
    main()