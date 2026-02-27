import re
import unicodedata

def remover_acentos(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")

def formatar_cpf(cpf: str) -> str:
    cpf = re.sub(r'\D', '', cpf)[:11]
    if len(cpf) != 11:
        return cpf  # retorna sem formatação se não tiver 11 dígitos
    return re.sub(r'(\d{3})(\d{3})(\d{3})(\d{2})', r'\1.\2.\3-\4', cpf)

def formatar_rg(rg: str) -> str:
    rg = re.sub(r'\D', '', rg)[:9]
    return re.sub(r'(\d{2})(\d{3})(\d{3})(\d?)', r'\1.\2.\3-\4', rg)