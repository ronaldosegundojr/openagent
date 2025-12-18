from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import json
import time
from typing import Dict, Any

class LLMServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 1234):
        self.host = host
        self.port = port
        self.enable_cors = True
        self.app = Flask(__name__)
        self.model_manager = None 
        self.server_thread = None
        self.running = False
        self._setup_routes()
    
    def _setup_routes(self):
        @self.app.route('/v1/models', methods=['GET'])
        def list_models():
            if not self.model_manager: return jsonify({"error": "Manager not initialized"}), 500
            models = self.model_manager.list_local_models()
            return jsonify({
                "object": "list",
                "data": [{"id": m["id"], "object": "model", "owned_by": "local"} for m in models]
            })
        
        @self.app.route('/v1/chat/completions', methods=['POST'])
        def chat_completions():
            try:
                data = request.get_json()
                messages = data.get('messages', [])
                
                # Formata simples para o prompt
                prompt = ""
                for msg in messages:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    prompt += f"{role}: {content}\n"
                prompt += "assistant: "
                
                # Gera usando o manager
                response_text = self.model_manager.generate_text(
                    prompt, 
                    max_tokens=data.get('max_tokens', 1024),
                    temperature=data.get('temperature', 0.7)
                )
                
                return jsonify({
                    "id": f"chatcmpl-{int(time.time())}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": self.model_manager.get_active_model() or "local",
                    "choices": [{
                        "index": 0,
                        "message": {"role": "assistant", "content": response_text},
                        "finish_reason": "stop"
                    }]
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500

    def start(self):
        if self.running: return
        
        if self.enable_cors:
            CORS(self.app)
            
        def run():
            # Desativa o logging padrão do Flask para o terminal ficar limpo (estética hacker)
            import logging
            log = logging.getLogger('werkzeug')
            log.setLevel(logging.ERROR)
            self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
            
        self.server_thread = threading.Thread(target=run, daemon=True)
        self.server_thread.start()
        self.running = True
    
    def stop(self):
        self.running = False