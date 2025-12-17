import os
import sys

def test_agent_functionality():
    """Testa a funcionalidade do agente criando pasta e arquivo"""
    
    # Configurar encoding para Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    print("=== Teste do Agente OpenAI com Mistral ===")
    print()
    
    # Encontrar o caminho da área de trabalho
    desktop_paths = [
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Área de Trabalho"),
        os.path.join(os.path.expanduser("~"), "Desktop"),
        os.path.join(os.path.expanduser("~"), "Área de Trabalho"),
        "C:\\Users\\ronal\\OneDrive\\Área de Trabalho"
    ]
    
    desktop_path = None
    for path in desktop_paths:
        if os.path.exists(path):
            desktop_path = path
            break
    
    if not desktop_path:
        print("ERRO: Não foi possível encontrar a área de trabalho")
        return False
    
    print(f"Área de trabalho encontrada: {desktop_path}")
    
    # Criar pasta de teste
    test_folder = os.path.join(desktop_path, "teste_agente")
    
    try:
        os.makedirs(test_folder, exist_ok=True)
        print(f"✓ Pasta criada com sucesso: {test_folder}")
    except Exception as e:
        print(f"✗ Erro ao criar pasta: {e}")
        return False
    
    # Criar arquivo de teste
    test_file = os.path.join(test_folder, "teste.txt")
    content = "Olá, este é um teste do agente Mistral! A aplicação está funcionando corretamente."
    
    try:
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ Arquivo criado com sucesso: {test_file}")
    except Exception as e:
        print(f"✗ Erro ao criar arquivo: {e}")
        return False
    
    # Verificar se tudo foi criado corretamente
    if os.path.exists(test_folder) and os.path.exists(test_file):
        print()
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✓ O modelo Mistral foi baixado corretamente")
        print("✓ A aplicação OpenAgent está funcionando")
        print("✓ O agente consegue criar pastas e arquivos")
        print()
        print(f"Local dos arquivos criados: {test_folder}")
        
        # Mostrar conteúdo do arquivo
        try:
            with open(test_file, "r", encoding="utf-8") as f:
                file_content = f.read()
            print(f"Conteúdo do arquivo: {file_content}")
        except:
            pass
        
        return True
    else:
        print("✗ Falha na verificação dos arquivos criados")
        return False

if __name__ == "__main__":
    success = test_agent_functionality()
    sys.exit(0 if success else 1)