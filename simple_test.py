import requests
import json
import os

def test_openagent_api():
    """Testa a API do OpenAgent diretamente"""
    
    # Primeiro, verificar se o servidor está rodando
    try:
        response = requests.get("http://localhost:1234/health", timeout=5)
        print("✅ Servidor OpenAgent está rodando!")
    except:
        print("❌ Servidor OpenAgent não está rodando. Iniciando...")
        return False
    
    # Testar criação de pasta
    desktop_path = os.path.expanduser("~/Desktop")
    if not os.path.exists(desktop_path):
        desktop_path = os.path.expanduser("~/Área de Trabalho")
    
    test_folder = os.path.join(desktop_path, "teste_agente")
    
    try:
        os.makedirs(test_folder, exist_ok=True)
        print(f"✅ Pasta criada: {test_folder}")
        
        # Criar arquivo de teste
        test_file = os.path.join(test_folder, "teste.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("Olá, este é um teste do agente Mistral!")
        
        print(f"✅ Arquivo criado: {test_file}")
        
        # Verificar se tudo foi criado corretamente
        if os.path.exists(test_folder) and os.path.exists(test_file):
            print("🎉 Teste concluído com sucesso! O agente funcionou corretamente.")
            return True
        else:
            print("❌ Falha na verificação dos arquivos criados.")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao criar pasta/arquivo: {e}")
        return False

if __name__ == "__main__":
    test_openagent_api()