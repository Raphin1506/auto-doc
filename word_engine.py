import os
from docxtpl import DocxTemplate

class GeradorWord:
    @staticmethod
    def criar_termo(caminho_modelo: str, caminho_salvar: str, dados: dict):
        """
        Abre o modelo Word, injeta os dados do dicionário e salva o novo arquivo.
        """
        try:
            if not os.path.exists(caminho_modelo):
                raise FileNotFoundError("O arquivo modelo não foi encontrado.")

            # O DocxTemplate lê o arquivo e entende onde estão as variáveis
            doc = DocxTemplate(caminho_modelo)
            
            # A função render substitui tudo de uma vez, mantendo negrito, itálico, tabelas, etc.
            doc.render(dados)
            
            # Salva o arquivo final preenchido
            doc.save(caminho_salvar)
            
        except Exception as e:
            raise Exception(f"Erro ao processar o Word: {str(e)}")