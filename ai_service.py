import spacy
import re
import os

class ServicoIA:
    def __init__(self):
        # Tenta carregar o seu modelo treinado. Se não achar, avisa.
        if os.path.exists("modelo_autodoc"):
            self.nlp = spacy.load("modelo_autodoc")
        else:
            self.nlp = None

    def analisar_texto(self, texto: str) -> dict:
        """
        Recebe um texto bagunçado e extrai TUDO usando a abordagem Híbrida:
        RegEx para padrões exatos (CPF, CEP) + IA para contextos (Nome, Equipamento).
        """
        dados_extraidos = {
            "nome": "",
            "equipamento": "",
            "departamento": "",
            "cpf": "",
            "rg": "",
            "cep": "",
            "data": "",
            "serie": ""
        }

        # 1. O FRANCO-ATIRADOR (RegEx para padrões exatos)
        
        # Procura CPF (com ou sem pontuação)
        match_cpf = re.search(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\b\d{11}\b', texto)
        if match_cpf:
            dados_extraidos["cpf"] = match_cpf.group()
                      
        # Procura RG (Padrão 9 dígitos seguidos ou formatado XX.XXX.XXX-X)
        match_rg = re.search(r'\b\d{1,2}\.\d{3}\.\d{3}-[0-9Xx]\b|\b\d{9}\b', texto)
        if match_rg:
            dados_extraidos["rg"] = match_rg.group()
            
        # Procura CEP (com ou sem traço)
        match_cep = re.search(r'\b\d{5}-\d{3}\b|\b\d{8}\b', texto)
        if match_cep:
            dados_extraidos["cep"] = match_cep.group()

        # Procura Data (formato DD/MM/AAAA)
        match_data = re.search(r'\b\d{2}/\d{2}/\d{4}\b', texto)
        if match_data:
            dados_extraidos["data"] = match_data.group()

        # Procura Série/Patrimônio (Exemplo: 5 a 8 letras ou números maiúsculos juntos)
        # Ajuste esse padrão dependendo de como são as Service Tags / Séries da sua empresa
        match_serie = re.search(r'\b(?:[A-Z]+[0-9-]|[0-9-]+[A-Z])[A-Z0-9-]*\b', texto)
        if match_serie:
            dados_extraidos["serie"] = match_serie.group()

        # 2. O DETETIVE (Inteligência Artificial para contextos)
        if self.nlp:
            doc = self.nlp(texto)
            for ent in doc.ents:
                if ent.label_ == "PESSOA" and not dados_extraidos["nome"]:
                    dados_extraidos["nome"] = ent.text
                elif ent.label_ == "EQUIPAMENTO" and not dados_extraidos["equipamento"]:
                    dados_extraidos["equipamento"] = ent.text
                elif ent.label_ == "DEPARTAMENTO" and not dados_extraidos["departamento"]:
                    dados_extraidos["departamento"] = ent.text

        return dados_extraidos

# Teste rápido se você rodar só esse arquivo no terminal
if __name__ == "__main__":
    texto_chamado = """
    Favor emitir termo para o notebook Lenovo, Service Tag JX90KL, 
    que será entregue para o analista Carlos do Financeiro. 
    Os dados dele são CPF 123.456.789-00, e o CEP de entrega é 01001-000. Data: 25/10/2023.
    """
    
    servico = ServicoIA()
    resultado = servico.analisar_texto(texto_chamado)
    
    print("--- RESULTADO DA EXTRAÇÃO HÍBRIDA ---")
    for chave, valor in resultado.items():
        print(f"{chave.upper()}: {valor}")