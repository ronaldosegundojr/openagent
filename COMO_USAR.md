# Guia de Início Rápido - OpenAgent

O OpenAgent foi desenhado para ser simples e poderoso.

## Passo 1: Configuração Inicial
Após instalar o `requirements.txt`, rode o comando principal:
`python -m openagent.core`

## Passo 2: Baixando seu Primeiro Modelo
Se você ainda não tem um modelo, use a busca:
`/search Mistral-7B`
Escolha um ID e baixe:
`/download TheBloke/Mistral-7B-Instruct-v0.2-GGUF`

## Passo 3: Carregando
Liste os modelos para confirmar o download:
`/models`
Carregue o modelo:
`/load TheBloke/Mistral-7B-Instruct-v0.2-GGUF`

## Passo 4: Hardware e Performance
Se o PC estiver lento, reduza as threads:
`/config threads 4`
Se tiver placa de vídeo (NVIDIA), use a GPU:
`/config gpu -1`

## Passo 5: Conversando com o Agente
Peça tarefas como:
- "Crie um script python que liste os arquivos desta pasta"
- "Leia o arquivo README.md e faça um resumo"
- "Edite o arquivo config.json mudando a porta para 8080"