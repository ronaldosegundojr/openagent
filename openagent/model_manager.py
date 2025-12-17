import os
import json
import requests
import subprocess
import threading
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import time

class ModelManager:
    def __init__(self, models_dir: str = "./models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.config_file = self.models_dir / "config.json"
        self.loaded_models = {}
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {"models": {}, "active_model": None}
    
    def _save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def search_models(self, query: str = "", source: str = "all") -> List[Dict]:
        """Busca modelos disponíveis no HuggingFace e Ollama"""
        models = []
        
        if source in ["all", "huggingface"]:
            models.extend(self._search_huggingface_models(query))
        
        if source in ["all", "ollama"]:
            models.extend(self._search_ollama_models(query))
        
        return models[:20]
    
    def _search_huggingface_models(self, query: str = "") -> List[Dict]:
        """Busca modelos no HuggingFace"""
        try:
            url = "https://huggingface.co/api/models"
            params = {"search": query, "limit": 50} if query else {"limit": 50}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                models = response.json()
                filtered_models = []
                
                for model in models:
                    model_id = model.get("modelId", "")
                    if any(keyword in model_id.lower() 
                          for keyword in ["gguf", "ggml", "quantized", "q4", "q8", "q3"]):
                        
                    capabilities = self._detect_model_capabilities(model_id, model.get("tags", []))
                    
                    filtered_models.append({
                        "id": model_id,
                        "name": model_id,
                        "description": model.get("description", ""),
                        "downloads": model.get("downloads", 0),
                        "likes": model.get("likes", 0),
                        "size": self._estimate_model_size(model_id),
                        "source": "huggingface",
                        "capabilities": capabilities,
                        "tags": model.get("tags", [])
                    })
                
                return filtered_models
        except Exception as e:
            print(f"Erro ao buscar modelos HuggingFace: {e}")
        
        return []
    
    def _search_ollama_models(self, query: str = "") -> List[Dict]:
        """Busca modelos no Ollama"""
        try:
            url = "https://registry.ollama.ai/v2/repositories"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                repositories = response.json().get("repositories", [])
                models = []
                
                for repo in repositories:
                    if query.lower() in repo.lower():
                        model_info = self._get_ollama_model_info(repo)
                        if model_info:
                            models.append(model_info)
                
                return models
        except Exception as e:
            print(f"Erro ao buscar modelos Ollama: {e}")
        
        return self._get_popular_ollama_models()
    
    def _get_ollama_model_info(self, model_name: str) -> Optional[Dict]:
        """Obtém informações detalhadas de um modelo Ollama"""
        try:
            url = f"https://registry.ollama.ai/v2/repositories/{model_name}/tags"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                tags = response.json().get("tags", [])
                if tags:
                    latest_tag = tags[0]
                    capabilities = self._detect_ollama_capabilities(model_name, latest_tag)
                    
                    return {
                        "id": f"ollama/{model_name}",
                        "name": model_name,
                        "description": f"Modelo Ollama: {model_name}",
                        "downloads": 0,
                        "likes": 0,
                        "size": latest_tag.get("size", "Unknown"),
                        "source": "ollama",
                        "capabilities": capabilities,
                        "tags": latest_tag.get("labels", {})
                    }
        except Exception:
            pass
        
        return None
    
    def _detect_model_capabilities(self, model_id: str, tags: List[str]) -> Dict[str, bool]:
        """Detecta capacidades do modelo baseado no nome e tags"""
        capabilities = {
            "tools": False,
            "reasoning": False,
            "vision": False,
            "code": False,
            "chat": False,
            "multimodal": False
        }
        
        model_lower = model_id.lower()
        tags_lower = [tag.lower() for tag in tags]
        
        # Detecção de capacidades
        if any(keyword in model_lower for keyword in ["instruct", "chat", "conversation"]):
            capabilities["chat"] = True
        
        if any(keyword in model_lower for keyword in ["tool", "function", "agent"]):
            capabilities["tools"] = True
        
        if any(keyword in model_lower for keyword in ["reason", "think", "cot", "chain"]):
            capabilities["reasoning"] = True
        
        if any(keyword in model_lower for keyword in ["vision", "vqa", "multimodal", "clip"]):
            capabilities["vision"] = True
            capabilities["multimodal"] = True
        
        if any(keyword in model_lower for keyword in ["code", "coder", "python", "javascript"]):
            capabilities["code"] = True
        
        if any(keyword in tags_lower for keyword in ["tool-use", "function-calling", "agent"]):
            capabilities["tools"] = True
        
        if any(keyword in tags_lower for keyword in ["vision", "multimodal", "image"]):
            capabilities["vision"] = True
            capabilities["multimodal"] = True
        
        return capabilities
    
    def _detect_ollama_capabilities(self, model_name: str, tag_info: Dict) -> Dict[str, bool]:
        """Detecta capacidades de modelos Ollama"""
        capabilities = {
            "tools": False,
            "reasoning": False,
            "vision": False,
            "code": False,
            "chat": False,
            "multimodal": False
        }
        
        model_lower = model_name.lower()
        labels = tag_info.get("labels", {})
        
        # Análise baseada no nome do modelo
        if any(keyword in model_lower for keyword in ["llava", "vision", "multimodal"]):
            capabilities["vision"] = True
            capabilities["multimodal"] = True
        
        if any(keyword in model_lower for keyword in ["codellama", "code", "coder"]):
            capabilities["code"] = True
        
        if "chat" in model_lower:
            capabilities["chat"] = True
        
        # Análise baseada nas labels
        if labels.get("capabilities"):
            caps = labels["capabilities"].lower()
            if "tool" in caps:
                capabilities["tools"] = True
            if "vision" in caps:
                capabilities["vision"] = True
            if "code" in caps:
                capabilities["code"] = True
        
        return capabilities
    
    def _get_popular_models(self) -> List[Dict]:
        """Retorna modelos populares para download"""
        return [
            {
                "id": "TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
                "name": "Mistral 7B Instruct (GGUF)",
                "description": "Modelo Mistral 7B otimizado para inferência local",
                "downloads": 1000000,
                "likes": 5000,
                "size": "4.1GB",
                "source": "huggingface",
                "capabilities": {"tools": True, "reasoning": True, "vision": False, "code": True, "chat": True, "multimodal": False}
            },
            {
                "id": "TheBloke/Llama-2-7B-Chat-GGUF",
                "name": "Llama 2 7B Chat (GGUF)",
                "description": "Modelo Llama 2 7B para conversação",
                "downloads": 800000,
                "likes": 4000,
                "size": "3.8GB",
                "source": "huggingface",
                "capabilities": {"tools": False, "reasoning": False, "vision": False, "code": False, "chat": True, "multimodal": False}
            },
            {
                "id": "openai/whisper-large-v3",
                "name": "Whisper Large V3",
                "description": "Modelo de reconhecimento de fala",
                "downloads": 500000,
                "likes": 2000,
                "size": "3.0GB",
                "source": "huggingface",
                "capabilities": {"tools": False, "reasoning": False, "vision": False, "code": False, "chat": False, "multimodal": True}
            }
        ]
    
    def _get_popular_ollama_models(self) -> List[Dict]:
        """Retorna modelos populares do Ollama"""
        return [
            {
                "id": "ollama/llama3.2",
                "name": "Llama 3.2",
                "description": "Modelo Llama 3.2 do Ollama",
                "downloads": 0,
                "likes": 0,
                "size": "4.7GB",
                "source": "ollama",
                "capabilities": {"tools": True, "reasoning": True, "vision": False, "code": True, "chat": True, "multimodal": False}
            },
            {
                "id": "ollama/llava",
                "name": "LLaVA",
                "description": "Modelo com visão do Ollama",
                "downloads": 0,
                "likes": 0,
                "size": "4.8GB",
                "source": "ollama",
                "capabilities": {"tools": False, "reasoning": False, "vision": True, "code": False, "chat": True, "multimodal": True}
            },
            {
                "id": "ollama/codellama",
                "name": "CodeLlama",
                "description": "Modelo especializado em código do Ollama",
                "downloads": 0,
                "likes": 0,
                "size": "3.8GB",
                "source": "ollama",
                "capabilities": {"tools": True, "reasoning": True, "vision": False, "code": True, "chat": True, "multimodal": False}
            }
        ]
    
    def _estimate_model_size(self, model_id: str) -> str:
        """Estima o tamanho do modelo baseado no nome"""
        if "7b" in model_id.lower():
            return "~4GB"
        elif "13b" in model_id.lower():
            return "~8GB"
        elif "70b" in model_id.lower():
            return "~40GB"
        return "~2GB"
    
    def download_model(self, model_id: str, progress_callback=None) -> bool:
        """Baixa um modelo do HuggingFace"""
        try:
            print(f"Baixando modelo: {model_id}")
            
            model_path = self.models_dir / model_id.replace("/", "_")
            model_path.mkdir(exist_ok=True)
            
            if progress_callback:
                progress_callback(f"Iniciando download de {model_id}")
            
            # Simulação de download (na implementação real, usaria huggingface_hub)
            for i in range(10):
                time.sleep(0.5)
                if progress_callback:
                    progress_callback(f"Baixando... {i*10}%")
            
            # Criar arquivo de modelo simulado
            model_file = model_path / "model.gguf"
            with open(model_file, 'w') as f:
                f.write(f"Modelo simulado: {model_id}")
            
            self.config["models"][model_id] = {
                "path": str(model_file),
                "downloaded_at": time.time(),
                "size": model_file.stat().st_size
            }
            self._save_config()
            
            if progress_callback:
                progress_callback("Download concluído!")
            
            return True
            
        except Exception as e:
            print(f"Erro ao baixar modelo: {e}")
            return False
    
    def list_local_models(self) -> List[Dict]:
        """Lista modelos locais disponíveis"""
        models = []
        for model_id, info in self.config.get("models", {}).items():
            models.append({
                "id": model_id,
                "path": info["path"],
                "size": info.get("size", 0),
                "downloaded_at": info.get("downloaded_at", 0)
            })
        return models
    
    def load_model(self, model_id: str) -> bool:
        """Carrega um modelo para uso"""
        if model_id in self.loaded_models:
            return True
        
        if model_id not in self.config.get("models", {}):
            print(f"Modelo {model_id} não encontrado localmente")
            return False
        
        try:
            # Simulação de carregamento do modelo
            print(f"Carregando modelo: {model_id}")
            self.loaded_models[model_id] = {
                "loaded_at": time.time(),
                "status": "ready"
            }
            self.config["active_model"] = model_id
            self._save_config()
            return True
        except Exception as e:
            print(f"Erro ao carregar modelo: {e}")
            return False
    
    def unload_model(self, model_id: str):
        """Descarrega um modelo da memória"""
        if model_id in self.loaded_models:
            del self.loaded_models[model_id]
            if self.config.get("active_model") == model_id:
                self.config["active_model"] = None
            self._save_config()
    
    def get_active_model(self) -> Optional[str]:
        """Retorna o modelo atualmente ativo"""
        return self.config.get("active_model")
    
    def generate_text(self, prompt: str, model_id: Optional[str] = None, **kwargs) -> str:
        """Gera texto usando o modelo carregado"""
        target_model = model_id or self.get_active_model()
        
        if not target_model:
            return "Nenhum modelo carregado"
        
        if target_model not in self.loaded_models:
            return f"Modelo {target_model} não está carregado"
        
        # Simulação de geração de texto
        time.sleep(0.5)
        return f"Resposta gerada pelo modelo {target_model} para: {prompt[:50]}..."