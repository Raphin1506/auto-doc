# 🧾 AutoDoc V2 - Gerador de Termos Inteligente

O **AutoDoc** é uma aplicação em Python com interface gráfica moderna desenvolvida em **CustomTkinter** que automatiza a geração de documentos do Word (`.docx`). 

Na sua versão 2.0, o projeto passou por uma grande refatoração arquitetural, ganhando um **Motor de Inteligência Artificial Híbrido** (Processamento de Linguagem Natural com `spaCy` + Expressões Regulares) que extrai dados automaticamente de textos de chamados de TI, preenchendo o formulário sem intervenção humana.

---

## 🚀 Novidades da V2 (Arquitetura e IA)
- **Extração Híbrida Inteligente:** Cole o texto bagunçado de um chamado de TI e a IA identifica e separa automaticamente: *Nome, Equipamento, Departamento, CPF, RG, CEP, Data e Número de Série*.
- **Motor de Word Inteligente (`docxtpl`):** Substituição de tags (ex: `{{ nome }}`) que preserva 100% da formatação original do documento (negritos, tabelas, fontes).
- **Treinamento de NER Customizado:** O modelo do spaCy foi treinado localmente com dados específicos do dia a dia de TI para reconhecer equipamentos e departamentos.
- **Arquitetura Modular:** Separação clara de responsabilidades (UI, Regras de Negócio, IA e Manipulação de Word).

---

## ⚙️ Funcionalidades Principais

- 🤖 **"Campo Mágico" com IA:** Preenchimento automático de todo o formulário a partir de um texto bruto.
- 🔎 **Consulta via API:** Busca automática de logradouro, bairro e cidade usando a API do ViaCEP.
- 🖤 **Interface Moderna:** Modo escuro nativo e design responsivo.
- 📅 **Calendário Interativo:** Seleção de datas de forma visual.
- 📂 **Templates Dinâmicos:** Escolha de modelos de documento `.docx` diretamente de uma pasta configurada.
- 🪪 **Validação e Formatação:** Máscaras automáticas para CPF e RG.

---

## 📦 Dependências

O projeto utiliza as seguintes bibliotecas Python:

- `customtkinter`
- `tkcalendar`
- `docxtpl`
- `requests`
- `spacy`

---

## 🛠️ Como Instalar e Rodar

1. Clone este repositório:
`git clone https://github.com/Raphin1506/auto-doc.git`
`cd auto-doc`

2. Instale as dependências do projeto:
`pip install -r requirements.txt`

3. **Importante:** Baixe o modelo de linguagem em Português para o cérebro da IA (`spaCy`):
`python -m spacy download pt_core_news_sm`

4. Execute o aplicativo:
`python main.py`

*(Dica: O projeto já inclui a pasta `modelo_autodoc` com os pesos da IA treinados para o contexto de TI).*

---

## 👨‍💻 Desenvolvido por:

**Raphael Vinicius** 💻 Focado em automação, arquitetura de software e soluções inteligentes com **Python**.  
📫 [LinkedIn](https://www.linkedin.com/in/raphael-vin%C3%ADcius-amaral-de-andrade-784802233/) | [GitHub](https://github.com/Raphin1506)