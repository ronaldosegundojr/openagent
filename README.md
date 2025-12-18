# 🟢 OpenAgent - Agente de IA Local de Elite

OpenAgent é um ecossistema completo para rodar modelos de linguagem (LLMs) localmente, funcionando como um **LM Studio de Terminal**. Ele permite baixar modelos GGUF, subir um servidor API compatível com OpenAI e interagir com um agente autônomo capaz de manipular arquivos, áudio e imagens.

## 🚀 Funcionalidades Principais

- **Terminal Hacker Style**: Interface rica e colorida usando o tema Dracula.
- **100% Local**: Sem dependências de nuvem ou APIs pagas (opcional).
- **Gerenciador de Modelos**: Busca e download direto do Hugging Face.
- **Servidor OpenAI**: API local (`llama-cpp-python`) integrada.
- **Agente Autônomo**: Capaz de ler, editar, criar arquivos e executar comandos.
- **Multimodal**: Suporte para transcrição de áudio e processamento de imagens.

## 🛠️ Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/ronaldosegundojr/openagent.git
   cd openagent
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Como Usar

Para iniciar o agente em modo interativo:
```bash
python -m openagent.core
```

### Comandos de Terminal (/Slash Commands)

Dentro do shell do OpenAgent, você pode usar:

- `/search <query>`: Busca modelos GGUF no Hugging Face.
- `/download <repo_id>`: Baixa um modelo específico.
- `/models`: Lista seus modelos baixados localmente.
- `/load <id>`: Carrega o modelo na memória com as configs de hardware.
- `/config`: Abre o menu de configurações técnicas.
- `/prompt`: Troca o estilo de personalidade do agente (Hacker, Analista, etc).
- `/status`: Mostra informações do servidor e hardware.
- `/quit`: Encerra o agente e o servidor.

## ⚙️ Configurações Avançadas

Você pode ajustar o hardware através do comando `/config`:

- `host`: IP do servidor (ex: 127.0.0.1 ou 0.0.0.0).
- `port`: Porta de comunicação.
- `threads`: Quantidade de threads da CPU para processamento.
- `gpu`: Camadas enviadas para a GPU (use `-1` para auto).
- `context`: Tamanho da janela de contexto.
- `temp`: Temperatura do modelo (criatividade).
- `mcp`: Habilitar/Desabilitar suporte a plugins MCP.

## 📄 Licença
Distribuído sob a licença MIT. Consulte `LICENSE` para mais informações.