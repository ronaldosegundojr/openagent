import json
import os
import sys
from openai import OpenAI

# Configurar encoding para Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Conecta no LM Studio
client = OpenAI(
    api_key="dummy",
    base_url="http://localhost:1234/v1"
)

# ========= TOOLS =========

def write_file(path: str, content: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Arquivo criado: {os.path.abspath(path)}"

def create_folder(path: str):
    os.makedirs(path, exist_ok=True)
    return f"Pasta criada: {os.path.abspath(path)}"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Cria ou sobrescreve um arquivo no sistema",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_folder",
            "description": "Cria uma pasta no sistema",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        }
    }
]

# ========= LOOP DO AGENTE =========

messages = [
    {
        "role": "system",
        "content": (
            "Você é um agente com permissão para criar arquivos e pastas locais. "
            "Quando precisar criar algo, use as tools write_file ou create_folder. "
            "Responda em português."
        )
    }
]

def test_agent():
    """Função para testar o agente automaticamente"""
    user_request = "Crie uma pasta chamada 'teste_agente' na área de trabalho do usuário e dentro dela crie um arquivo chamado 'teste.txt' com o conteúdo 'Olá, este é um teste do agente Mistral!'"
    
    messages.append({"role": "user", "content": user_request})
    
    print(f"Usuário: {user_request}")
    
    response = client.chat.completions.create(
        model="mistralai/Ministral-3-3B-Instruct-2512-GGUF",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )
    
    msg = response.choices[0].message
    
    # Se a LLM pedir uma tool
    if msg.tool_calls:
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            
            if call.function.name == "write_file":
                result = write_file(**args)
            elif call.function.name == "create_folder":
                result = create_folder(**args)
            else:
                result = "Função desconhecida"
            
            messages.append(msg)
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result
            })
            
            print(f"🛠️ {result}")
    else:
        messages.append({"role": "assistant", "content": msg.content})
        print(f"🤖 {msg.content}")

if __name__ == "__main__":
    test_agent()