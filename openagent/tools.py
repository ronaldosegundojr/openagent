import os
import json
import subprocess
import shutil
import glob
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import base64
from PIL import Image
import io

class FileSystemTools:
    """Ferramentas para manipulação de arquivos e diretórios"""
    
    @staticmethod
    def read_file(path: str, encoding: str = "utf-8") -> str:
        """Lê o conteúdo de um arquivo"""
        try:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
        except Exception as e:
            return f"Erro ao ler arquivo: {str(e)}"
    
    @staticmethod
    def write_file(path: str, content: str, encoding: str = "utf-8") -> str:
        """Cria ou sobrescreve um arquivo"""
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", encoding=encoding) as f:
                f.write(content)
            return f"Arquivo criado com sucesso: {os.path.abspath(path)}"
        except Exception as e:
            return f"Erro ao criar arquivo: {str(e)}"
    
    @staticmethod
    def append_file(path: str, content: str, encoding: str = "utf-8") -> str:
        """Adiciona conteúdo ao final de um arquivo"""
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "a", encoding=encoding) as f:
                f.write(content)
            return f"Conteúdo adicionado ao arquivo: {os.path.abspath(path)}"
        except Exception as e:
            return f"Erro ao adicionar conteúdo: {str(e)}"
    
    @staticmethod
    def delete_file(path: str) -> str:
        """Exclui um arquivo"""
        try:
            if os.path.exists(path):
                os.remove(path)
                return f"Arquivo excluído: {path}"
            else:
                return f"Arquivo não encontrado: {path}"
        except Exception as e:
            return f"Erro ao excluir arquivo: {str(e)}"
    
    @staticmethod
    def list_directory(path: str = ".", show_hidden: bool = False) -> Dict[str, Any]:
        """Lista conteúdo de um diretório"""
        try:
            if not os.path.exists(path):
                return {"error": f"Diretório não encontrado: {path}"}
            
            items = []
            for item in os.listdir(path):
                if not show_hidden and item.startswith('.'):
                    continue
                
                item_path = os.path.join(path, item)
                stat = os.stat(item_path)
                
                items.append({
                    "name": item,
                    "path": item_path,
                    "type": "directory" if os.path.isdir(item_path) else "file",
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "extension": os.path.splitext(item)[1] if os.path.isfile(item_path) else None
                })
            
            return {
                "path": os.path.abspath(path),
                "items": sorted(items, key=lambda x: (x["type"] == "file", x["name"].lower()))
            }
        except Exception as e:
            return {"error": f"Erro ao listar diretório: {str(e)}"}
    
    @staticmethod
    def create_directory(path: str) -> str:
        """Cria um diretório"""
        try:
            os.makedirs(path, exist_ok=True)
            return f"Diretório criado: {os.path.abspath(path)}"
        except Exception as e:
            return f"Erro ao criar diretório: {str(e)}"
    
    @staticmethod
    def delete_directory(path: str, recursive: bool = False) -> str:
        """Exclui um diretório"""
        try:
            if not os.path.exists(path):
                return f"Diretório não encontrado: {path}"
            
            if recursive:
                shutil.rmtree(path)
                return f"Diretório excluído recursivamente: {path}"
            else:
                os.rmdir(path)
                return f"Diretório excluído: {path}"
        except Exception as e:
            return f"Erro ao excluir diretório: {str(e)}"
    
    @staticmethod
    def copy_file(source: str, destination: str) -> str:
        """Copia um arquivo"""
        try:
            os.makedirs(os.path.dirname(destination) or ".", exist_ok=True)
            shutil.copy2(source, destination)
            return f"Arquivo copiado de {source} para {destination}"
        except Exception as e:
            return f"Erro ao copiar arquivo: {str(e)}"
    
    @staticmethod
    def move_file(source: str, destination: str) -> str:
        """Move um arquivo"""
        try:
            os.makedirs(os.path.dirname(destination) or ".", exist_ok=True)
            shutil.move(source, destination)
            return f"Arquivo movido de {source} para {destination}"
        except Exception as e:
            return f"Erro ao mover arquivo: {str(e)}"

    @staticmethod
    def edit_file(path: str, search_text: str, replace_text: str) -> str:
        """Substitui um texto específico dentro de um arquivo"""
        try:
            if not os.path.exists(path):
                return f"Erro: Arquivo {path} não encontrado."
            
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if search_text not in content:
                return f"Erro: Texto '{search_text}' não encontrado no arquivo."
            
            new_content = content.replace(search_text, replace_text)
            
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
                
            return f"Arquivo {path} editado com sucesso: '{search_text}' -> '{replace_text}'"
        except Exception as e:
            return f"Erro ao editar arquivo: {str(e)}"

class SystemTools:
    """Ferramentas de sistema e execução de comandos"""
    
    @staticmethod
    def execute_command(command: str, shell: bool = True, timeout: int = 30) -> Dict[str, Any]:
        """Executa um comando do sistema"""
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8'
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": command
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Comando excedeu o tempo limite de {timeout} segundos",
                "command": command
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Retorna informações do sistema"""
        try:
            import platform
            import psutil
            
            return {
                "platform": platform.platform(),
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": {
                    "total": psutil.disk_usage('/').total,
                    "used": psutil.disk_usage('/').used,
                    "free": psutil.disk_usage('/').free
                }
            }
        except Exception as e:
            return {"error": f"Erro ao obter informações do sistema: {str(e)}"}
    
    @staticmethod
    def get_working_directory() -> str:
        """Retorna o diretório de trabalho atual"""
        return os.getcwd()
    
    @staticmethod
    def change_directory(path: str) -> str:
        """Muda o diretório de trabalho"""
        try:
            os.chdir(path)
            return f"Diretório alterado para: {os.getcwd()}"
        except Exception as e:
            return f"Erro ao alterar diretório: {str(e)}"

class MediaTools:
    """Ferramentas para processamento de mídia"""
    
    @staticmethod
    def encode_image_to_base64(image_path: str, max_size: tuple = (1024, 1024)) -> Dict[str, Any]:
        """Codifica uma imagem para base64"""
        try:
            if not os.path.exists(image_path):
                return {"error": f"Arquivo de imagem não encontrado: {image_path}"}
            
            with Image.open(image_path) as img:
                # Redimensiona se necessário
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Converte para RGB se necessário
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Salva em buffer
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                buffer.seek(0)
                
                # Codifica para base64
                img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                return {
                    "success": True,
                    "base64": img_base64,
                    "format": "JPEG",
                    "size": img.size,
                    "original_size": os.path.getsize(image_path),
                    "encoded_size": len(img_base64)
                }
        except Exception as e:
            return {"error": f"Erro ao processar imagem: {str(e)}"}
    
    @staticmethod
    def get_image_info(image_path: str) -> Dict[str, Any]:
        """Retorna informações sobre uma imagem"""
        try:
            if not os.path.exists(image_path):
                return {"error": f"Arquivo de imagem não encontrado: {image_path}"}
            
            with Image.open(image_path) as img:
                return {
                    "success": True,
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "file_size": os.path.getsize(image_path)
                }
        except Exception as e:
            return {"error": f"Erro ao obter informações da imagem: {str(e)}"}

    @staticmethod
    def transcribe_audio(audio_path: str) -> str:
        """Transcreve um arquivo de áudio para texto (Simulado por agora)"""
        try:
            return f"Transcrição simulada do áudio {audio_path}: 'Esta é uma mensagem de voz do usuário pedindo para listar os arquivos.'"
        except Exception as e:
            return f"Erro ao transcrever áudio: {str(e)}"

class SearchTools:
    """Ferramentas de busca"""
    
    @staticmethod
    def search_files(pattern: str, path: str = ".", recursive: bool = True) -> List[str]:
        """Busca arquivos por padrão"""
        try:
            if recursive:
                search_pattern = os.path.join(path, "**", pattern)
                return glob.glob(search_pattern, recursive=True)
            else:
                search_pattern = os.path.join(path, pattern)
                return glob.glob(search_pattern)
        except Exception as e:
            return [f"Erro na busca: {str(e)}"]
    
    @staticmethod
    def search_in_files(search_term: str, path: str = ".", file_pattern: str = "*") -> Dict[str, List[Dict[str, Any]]]:
        """Busca texto dentro de arquivos"""
        try:
            results = {}
            files = SearchTools.search_files(file_pattern, path)
            
            for file_path in files:
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            
                            matches = []
                            for line_num, line in enumerate(lines, 1):
                                if search_term.lower() in line.lower():
                                    matches.append({
                                        "line": line_num,
                                        "content": line.strip(),
                                        "column": line.lower().find(search_term.lower())
                                    })
                            
                            if matches:
                                results[file_path] = matches
                    except Exception:
                        continue
            
            return {"results": results, "total_files_searched": len(files)}
        except Exception as e:
            return {"error": f"Erro na busca: {str(e)}"}

class ToolRegistry:
    """Registro central de todas as ferramentas"""
    
    def __init__(self):
        self.tools = {}
        self._register_all_tools()
    
    def _register_all_tools(self):
        """Registra todas as ferramentas disponíveis"""
        
        # FileSystem Tools
        self.tools["read_file"] = {
            "description": "Lê o conteúdo de um arquivo",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Caminho do arquivo"},
                    "encoding": {"type": "string", "default": "utf-8"}
                },
                "required": ["path"]
            }
        }
        
        self.tools["write_file"] = {
            "description": "Cria ou sobrescreve um arquivo",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Caminho do arquivo"},
                    "content": {"type": "string", "description": "Conteúdo do arquivo"},
                    "encoding": {"type": "string", "default": "utf-8"}
                },
                "required": ["path", "content"]
            }
        }
        
        self.tools["list_directory"] = {
            "description": "Lista conteúdo de um diretório",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "default": ".", "description": "Caminho do diretório"},
                    "show_hidden": {"type": "boolean", "default": False}
                }
            }
        }
        
        self.tools["execute_command"] = {
            "description": "Executa um comando do sistema",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Comando a ser executado"},
                    "timeout": {"type": "integer", "default": 30, "description": "Timeout em segundos"}
                },
                "required": ["command"]
            }
        }
        
        self.tools["encode_image_to_base64"] = {
            "description": "Codifica uma imagem para base64",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Caminho da imagem"},
                    "max_size": {"type": "array", "items": {"type": "integer"}, "default": [1024, 1024]}
                },
                "required": ["image_path"]
            }
        }
        
        self.tools["edit_file"] = {
            "description": "Edita um arquivo existente substituindo um texto por outro",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Caminue do arquivo"},
                    "search_text": {"type": "string", "description": "Texto a ser buscado"},
                    "replace_text": {"type": "string", "description": "Texto de substituição"}
                },
                "required": ["path", "search_text", "replace_text"]
            }
        }

        self.tools["search_files"] = {
            "description": "Busca arquivos por padrão",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Padrão de busca (ex: *.py)"},
                    "path": {"type": "string", "default": ".", "description": "Diretório de busca"},
                    "recursive": {"type": "boolean", "default": True}
                },
                "required": ["pattern"]
            }
        }

        self.tools["transcribe_audio"] = {
            "description": "Converte um arquivo de áudio (wav, mp3) em texto",
            "parameters": {
                "type": "object",
                "properties": {
                    "audio_path": {"type": "string", "description": "Caminho do arquivo de áudio"}
                },
                "required": ["audio_path"]
            }
        }
    
    def get_tool_definitions(self) -> List[Dict]:
        """Retorna definições das ferramentas no formato OpenAI"""
        definitions = []
        for name, tool in self.tools.items():
            definitions.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            })
        return definitions
    
    def execute_tool(self, tool_name: str, arguments: Dict) -> Any:
        """Executa uma ferramenta específica"""
        if tool_name == "read_file":
            return FileSystemTools.read_file(**arguments)
        elif tool_name == "write_file":
            return FileSystemTools.write_file(**arguments)
        elif tool_name == "list_directory":
            return FileSystemTools.list_directory(**arguments)
        elif tool_name == "execute_command":
            return SystemTools.execute_command(**arguments)
        elif tool_name == "encode_image_to_base64":
            return MediaTools.encode_image_to_base64(**arguments)
        elif tool_name == "search_files":
            return SearchTools.search_files(**arguments)
        else:
            return f"Ferramenta não encontrada: {tool_name}"