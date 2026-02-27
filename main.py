import sys
import os
from ui import AutoDocApp

def resource_path(relative_path):
    """ 
    Retorna o caminho absoluto para o recurso, 
    essencial para o PyInstaller encontrar ícones e pastas dentro do .exe 
    """
    try:
        # O PyInstaller cria uma pasta temporária em _MEIPASS ao rodar
        base_path = sys._MEIPASS
    except Exception:
        # Se estiver rodando em desenvolvimento (Python normal), usa a pasta atual
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    # 1. Definimos o caminho do ícone e da pasta de documentos
    caminho_icone = resource_path("icon.ico")
    caminho_doc = resource_path("doc")

    # 2. Inicializamos o App
    # Dica: Você pode passar esses caminhos como argumentos se quiser
    app = AutoDocApp()
    
    # 3. Aplicamos o ícone na janela principal (Windows puro)
    try:
        if os.path.exists(caminho_icone):
            app.iconbitmap(caminho_icone)
    except Exception as e:
        print(f"⚠️ Não foi possível carregar o ícone na barra de tarefas: {e}")

    app.mainloop()