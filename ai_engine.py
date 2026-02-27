import spacy
import random
from spacy.training.example import Example

# 1.DATASET MANUAL
# Formato: ("Texto do chamado", {"entities": [(letra_inicio, letra_fim, "CATEGORIA")]})
TRAIN_DATA = [
    ('A Maria do RH solicitou um novo mouse Logitech sem fio.', {'entities': [(32, 46, 'EQUIPAMENTO'), (2, 7, 'PESSOA'), (11, 13, 'DEPARTAMENTO')]}),
    ('Preparar um notebook Dell Latitude para o estagiário Pedro Silva.', {'entities': [(12, 34, 'EQUIPAMENTO'), (53, 64, 'PESSOA')]}),
    ('O monitor LG do setor Financeiro queimou a tela hoje cedo.', {'entities': [(22, 32, 'DEPARTAMENTO'), (2, 12, 'EQUIPAMENTO')]}),
    ('Preciso de um iPhone 13 para a diretora Ana Souza da Diretoria.', {'entities': [(40, 49, 'PESSOA'), (53, 62, 'DEPARTAMENTO'), (14, 23, 'EQUIPAMENTO')]}),
    ('Configurar o desktop Lenovo do analista Marcos na sala de TI.', {'entities': [(13, 27, 'EQUIPAMENTO'), (40, 46, 'PESSOA'), (58, 60, 'DEPARTAMENTO')]}),
    ('Realizar um termo para Raphael Vinícius Amaral de Andrade, com o CPF 12345678900', {'entities': [(23, 57, 'PESSOA')]}),
    ('Entregar o equipamento para João Carlos Batista do Nascimento no RH', {'entities': [(28, 61, 'PESSOA'), (65, 67, 'DEPARTAMENTO')]}),
    ('O usuário Luiz Fernando Costa de Oliveira solicitou a troca do notebook Dell', {'entities': [(10, 41, 'PESSOA'), (63, 76, 'EQUIPAMENTO')]}),
    ('Emitir termo de responsabilidade para Maria Eduarda de Albuquerque Machado', {'entities': [(38, 74, 'PESSOA')]}),
]

def treinar_modelo():
    print("1. Carregando modelo base 'pt_core_news_sm'...")
    nlp = spacy.load("pt_core_news_sm")

    # Pega a parte do cérebro responsável por nomes (NER)
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")

    # Ensina para a IA quais são as nossas novas categorias
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # Desliga as regras de gramática para ela focar 100% no treinamento de NER
    pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]

    print("\n2. Iniciando o treinamento (O estagiário está estudando)...")
    with nlp.disable_pipes(*other_pipes):
        # Prepara a IA para receber novos dados
        optimizer = nlp.resume_training()
        
        # Loop de Épocas (Vamos fazer ela ler tudo 30 vezes)
        for itn in range(30):
            random.shuffle(TRAIN_DATA)  # Embaralha os cadernos
            losses = {}
            
            for text, annotations in TRAIN_DATA:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                # O comando de aprendizado! dropout=0.5 significa 50% de esquecimento forçado
                nlp.update([example], drop=0.5, sgd=optimizer, losses=losses)
            
            # A cada 5 épocas, mostra como está a "taxa de erro" (loss)
            if itn % 5 == 0:
                print(f"Época {itn} - Taxa de erro (Losses): {losses}")

    # Ao final, salva a nova inteligência numa pasta chamada 'modelo_autodoc'
    print("\n3. Treinamento concluído! Salvando a nova IA na pasta 'modelo_autodoc'...")
    nlp.to_disk("modelo_autodoc")
    print("IA salva com sucesso!")

def testar_modelo():
    print("\n--- TESTANDO A IA COM UM TEXTO NOVO ---")
    # Carrega a IA que nós acabamos de salvar no HD
    nlp_treinado = spacy.load("modelo_autodoc")
    
    # Repare que esse texto NÃO estava no treinamento original!
    texto_teste = "Configurar um notebook Lenovo para o analista Carlos na sala do Financeiro."
    doc = nlp_treinado(texto_teste)
    
    for ent in doc.ents:
        print(f"Encontrei: {ent.text} | Categoria: {ent.label_}")

if __name__ == "__main__":
    treinar_modelo()
    testar_modelo()