import json
import os
from openai import OpenAI

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
    }
]

# ========= LOOP DO AGENTE =========

messages = [
    {
        "role": "system",
        "content": (
            "Você é um agente com permissão para criar arquivos locais. "
            "Quando precisar criar algo, use a tool write_file."
        )
    }
]

while True:
    user = input("\n🧑 Você: ")
    messages.append({"role": "user", "content": user})

    response = client.chat.completions.create(
        model="mistralai/ministral-3-14b-reasoning",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )

    msg = response.choices[0].message

    # Se a LLM pedir uma tool
    if msg.tool_calls:
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            result = write_file(**args)

            messages.append(msg)
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result
            })

            print("🛠️", result)
    else:
        messages.append({"role": "assistant", "content": msg.content})
        print("\n🤖", msg.content)
