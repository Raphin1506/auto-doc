import requests
import re

class CepService:
    @staticmethod
    def buscar_cep(cep_raw: str) -> dict:
        """
        Recebe um CEP, limpa os caracteres, consulta a API e devolve um dicionário com os dados.
        Se der erro, levanta uma exceção (que a interface vai capturar e mostrar no popup).
        """
        cep = re.sub(r'\D', '', cep_raw)
        
        if len(cep) != 8:
            raise ValueError("O CEP deve ter exatamente 8 dígitos.")
        
        try:
            # Faz a requisição com limite de 6 segundos para não travar o app
            resp = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=6)
            resp.raise_for_status()
            data = resp.json()
            
            if data.get("erro"):
                raise ValueError("CEP não encontrado na base de dados.")
                
            # Retorna um dicionário limpo e padronizado
            return {
                "logradouro": data.get("logradouro", ""),
                "complemento": data.get("complemento", ""),
                "bairro": data.get("bairro", ""),
                "cidade": data.get("localidade", ""),
                "uf": data.get("uf", "")
            }
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError("Erro de conexão com a internet ou servidor do ViaCEP fora do ar.")