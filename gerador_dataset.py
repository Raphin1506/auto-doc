import re

frases = [
    # --- Frases Antigas ---
    "A Maria do RH solicitou um novo mouse Logitech sem fio.",
    "Preparar um notebook Dell Latitude para o estagiário Pedro Silva.",
    "O monitor LG do setor Financeiro queimou a tela hoje cedo.",
    "Preciso de um iPhone 13 para a diretora Ana Souza da Diretoria.",
    "Configurar o desktop Lenovo do analista Marcos na sala de TI.",
    
    # --- FRASES NOVAS (O Treino Pesado) ---
    "Realizar um termo para Raphael Vinícius Amaral de Andrade, com o CPF 12345678900",
    "Entregar o equipamento para João Carlos Batista do Nascimento no RH",
    "O usuário Luiz Fernando Costa de Oliveira solicitou a troca do notebook Dell",
    "Emitir termo de responsabilidade para Maria Eduarda de Albuquerque Machado"
]

entidades_conhecidas = {
    # PESSOAS (Agora com nomes longos!)
    "Maria": "PESSOA",
    "Pedro Silva": "PESSOA",
    "Ana Souza": "PESSOA",
    "Marcos": "PESSOA",
    "Raphael Vinícius Amaral de Andrade": "PESSOA",
    "João Carlos Batista do Nascimento": "PESSOA",
    "Luiz Fernando Costa de Oliveira": "PESSOA",
    "Maria Eduarda de Albuquerque Machado": "PESSOA",
    
    # DEPARTAMENTOS
    "RH": "DEPARTAMENTO",
    "Financeiro": "DEPARTAMENTO",
    "Diretoria": "DEPARTAMENTO",
    "TI": "DEPARTAMENTO",
    
    # EQUIPAMENTOS
    "mouse Logitech": "EQUIPAMENTO",
    "notebook Dell Latitude": "EQUIPAMENTO",
    "monitor LG": "EQUIPAMENTO",
    "iPhone 13": "EQUIPAMENTO",
    "desktop Lenovo": "EQUIPAMENTO",
    "notebook Dell": "EQUIPAMENTO"
}


def gerar_treinamento():
    dataset_final = []
    
    # 1. Ordena o dicionário das maiores palavras para as menores
    # Assim ele prioriza achar "notebook Dell Latitude" antes de "notebook Dell"
    entidades_ordenadas = sorted(entidades_conhecidas.items(), key=lambda x: len(x[0]), reverse=True)
    
    for frase in frases:
        anotacoes = []
        caracteres_ocupados = set() # Guarda as posições que já foram preenchidas
        
        for palavra, categoria in entidades_ordenadas:
            for match in re.finditer(r'\b' + re.escape(palavra) + r'\b', frase, re.IGNORECASE):
                inicio = match.start()
                fim = match.end()
                
                # 2. Verifica se esse espaço já foi ocupado por uma palavra maior
                if not any(i in caracteres_ocupados for i in range(inicio, fim)):
                    anotacoes.append((inicio, fim, categoria))
                    # Bloqueia essas letras para não dar o Erro E103
                    caracteres_ocupados.update(range(inicio, fim))
        
        if anotacoes:
            dataset_final.append((frase, {"entities": anotacoes}))
            
    return dataset_final

if __name__ == "__main__":
    dados_prontos = gerar_treinamento()
    
    print("=== COPIE E COLE ISSO NO SEU ai_engine.py ===\n")
    print("TRAIN_DATA = [")
    for dado in dados_prontos:
        print(f"    {dado},")
    print("]")