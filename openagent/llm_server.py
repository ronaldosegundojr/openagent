from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import json
import time
from typing import Dict, Any
from .model_manager import ModelManager

class LLMServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 1234):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)
        self.model_manager = ModelManager()
        self.server_thread = None
        self.running = False
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Configura as rotas da API"""
        
        @self.app.route('/v1/models', methods=['GET'])
        def list_models():
            """Lista modelos disponíveis (compatível OpenAI)"""
            models = []
            for model in self.model_manager.list_local_models():
                models.append({
                    "id": model["id"],
                    "object": "model",
                    "created": int(model["downloaded_at"]),
                    "owned_by": "local"
                })
            
            return jsonify({
                "object": "list",
                "data": models
            })
        
        @self.app.route('/v1/chat/completions', methods=['POST'])
        def chat_completions():
            """Endpoint de chat completions (compatível OpenAI)"""
            try:
                data = request.get_json()
                
                # Extrai parâmetros
                messages = data.get('messages', [])
                model = data.get('model', self.model_manager.get_active_model())
                temperature = data.get('temperature', 0.7)
                max_tokens = data.get('max_tokens', 1000)
                stream = data.get('stream', False)
                
                # Processa mensagens para formato simples
                conversation = []
                for msg in messages:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    conversation.append(f"{role}: {content}")
                
                prompt = "\n".join(conversation)
                
                # Gera resposta
                response_text = self.model_manager.generate_text(
                    prompt, model, temperature=temperature, max_tokens=max_tokens
                )
                
                # Formata resposta compatível OpenAI
                response = {
                    "id": f"chatcmpl-{int(time.time())}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": response_text
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {
                        "prompt_tokens": len(prompt.split()),
                        "completion_tokens": len(response_text.split()),
                        "total_tokens": len(prompt.split()) + len(response_text.split())
                    }
                }
                
                return jsonify(response)
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/v1/completions', methods=['POST'])
        def completions():
            """Endpoint de completions (compatível OpenAI)"""
            try:
                data = request.get_json()
                prompt = data.get('prompt', '')
                model = data.get('model', self.model_manager.get_active_model())
                
                response_text = self.model_manager.generate_text(prompt, model)
                
                response = {
                    "id": f"cmpl-{int(time.time())}",
                    "object": "text_completion",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [{
                        "text": response_text,
                        "index": 0,
                        "logprobs": None,
                        "finish_reason": "stop"
                    }],
                    "usage": {
                        "prompt_tokens": len(prompt.split()),
                        "completion_tokens": len(response_text.split()),
                        "total_tokens": len(prompt.split()) + len(response_text.split())
                    }
                }
                
                return jsonify(response)
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/models/search', methods=['GET'])
        def search_models():
            """Busca modelos disponíveis para download"""
            query = request.args.get('q', '')
            models = self.model_manager.search_models(query)
            return jsonify({"models": models})
        
        @self.app.route('/api/models/download', methods=['POST'])
        def download_model():
            """Baixa um modelo"""
            data = request.get_json()
            model_id = data.get('model_id')
            
            if not model_id:
                return jsonify({"error": "model_id é obrigatório"}), 400
            
            def progress_callback(message):
                print(f"Download progress: {message}")
            
            success = self.model_manager.download_model(model_id, progress_callback)
            
            if success:
                return jsonify({"message": "Modelo baixado com sucesso"})
            else:
                return jsonify({"error": "Falha ao baixar modelo"}), 500
        
        @self.app.route('/api/models/load', methods=['POST'])
        def load_model():
            """Carrega um modelo"""
            data = request.get_json()
            model_id = data.get('model_id')
            
            if not model_id:
                return jsonify({"error": "model_id é obrigatório"}), 400
            
            success = self.model_manager.load_model(model_id)
            
            if success:
                return jsonify({"message": "Modelo carregado com sucesso"})
            else:
                return jsonify({"error": "Falha ao carregar modelo"}), 500
        
        @self.app.route('/api/models/unload', methods=['POST'])
        def unload_model():
            """Descarrega um modelo"""
            data = request.get_json()
            model_id = data.get('model_id')
            
            if model_id:
                self.model_manager.unload_model(model_id)
            
            return jsonify({"message": "Modelo descarregado"})
        
        @self.app.route('/api/models/active', methods=['GET'])
        def get_active_model():
            """Retorna o modelo ativo"""
            active = self.model_manager.get_active_model()
            return jsonify({"active_model": active})
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Verificação de saúde do servidor"""
            return jsonify({
                "status": "healthy",
                "timestamp": int(time.time()),
                "models_loaded": len(self.model_manager.loaded_models)
            })
    
    def start(self):
        """Inicia o servidor em uma thread separada"""
        if self.running:
            print("Servidor já está rodando")
            return
        
        def run_server():
            self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.running = True
        
        print(f"Servidor LLM iniciado em http://{self.host}:{self.port}")
    
    def stop(self):
        """Para o servidor"""
        self.running = False
        if self.server_thread:
            self.server_thread.join(timeout=5)
        print("Servidor LLM parado")
    
    def is_running(self) -> bool:
        """Verifica se o servidor está rodando"""
        return self.running