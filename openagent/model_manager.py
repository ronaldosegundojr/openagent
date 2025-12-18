import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
import time
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

class ModelManager:
    def __init__(self, models_dir: str = "./models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True, parents=True)
        self.config_file = self.models_dir / "models_config.json"
        self.loaded_model_instance = None
        self.active_model_id = None
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {"models": {}, "active_model": None}
    
    def _save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def search_models(self, query: str = "", source: str = "huggingface") -> List[Dict]:
        """Busca modelos GGUF no HuggingFace"""
        models = []
        try:
            url = "https://huggingface.co/api/models"
            params = {"search": f"{query} GGUF", "limit": 10}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                for model in response.json():
                    models.append({
                        "id": model.get("modelId"),
                        "downloads": model.get("downloads", 0)
                    })
        except Exception as e:
            pass
        return models

    def download_model(self, model_id: str, progress_callback=None) -> bool:
        """Baixa o arquivo GGUF do HuggingFace"""
        try:
            if progress_callback: progress_callback(f"Analisando {model_id}...")
            
            repo_id = model_id
            filename = None
            
            if ":" in model_id:
                repo_id, filename = model_id.split(":")
            else:
                url = f"https://huggingface.co/api/models/{repo_id}"
                resp = requests.get(url).json()
                filename = next((f["rfilename"] for f in resp.get("siblings", []) if f["rfilename"].lower().endswith(".gguf")), None)
            
            if not filename:
                if progress_callback: progress_callback("Nenhum .gguf encontrado.")
                return False

            path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                local_dir=self.models_dir / repo_id.replace("/", "_"),
                local_dir_use_symlinks=False
            )
            
            self.config["models"][model_id] = {
                "path": str(path),
                "repo": repo_id,
                "file": filename,
                "downloaded_at": time.time()
            }
            self._save_config()
            return True
        except Exception as e:
            return False

    def load_model(self, model_id: str, **kwargs) -> bool:
        """Carrega o modelo com parâmetros de hardware customizados"""
        if model_id not in self.config["models"]:
            return False
        
        model_path = self.config["models"][model_id]["path"]
        
        try:
            if self.loaded_model_instance:
                del self.loaded_model_instance
            
            # Aplica configurações: n_ctx, n_threads, n_gpu_layers
            self.loaded_model_instance = Llama(
                model_path=model_path,
                n_ctx=kwargs.get("n_ctx", 2048),
                n_threads=kwargs.get("n_threads", 4),
                n_gpu_layers=kwargs.get("n_gpu_layers", 0), # 0 = CPU, -1 = AUTO GPU
                verbose=False
            )
            self.active_model_id = model_id
            return True
        except Exception:
            return False

    def generate_text(self, prompt: str, **kwargs) -> str:
        if not self.loaded_model_instance:
            return "Erro: Modelo não carregado."
        
        try:
            # Geramos a resposta com os parâmetros de runtime
            output = self.loaded_model_instance(
                prompt,
                max_tokens=kwargs.get("max_tokens", 512),
                temperature=kwargs.get("temperature", 0.7),
                stop=["User:", "🧑", "🤖"]
            )
            return output["choices"][0]["text"].strip()
        except Exception as e:
            return f"Erro: {e}"

    def list_local_models(self) -> List[Dict]:
        return [{"id": k} for k in self.config["models"].keys()]

    def get_active_model(self) -> Optional[str]:
        return self.active_model_id