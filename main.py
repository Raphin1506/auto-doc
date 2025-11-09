import customtkinter as ctk
from tkinter import messagebox, filedialog
from tkcalendar import Calendar
from docx import Document
import re
import os
import requests
import threading
import unicodedata

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

def remover_acentos(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )

def formatar_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)
    cpf = cpf[:11]
    return re.sub(r'(\d{3})(\d{3})(\d{3})(\d{0,2})', r'\1.\2.\3-\4', cpf)

def formatar_rg(rg):
    rg = re.sub(r'\D', '', rg)
    rg = rg[:9]
    return re.sub(r'(\d{2})(\d{3})(\d{3})(\d{0,1})', r'\1.\2.\3-\4', rg)

def buscar_cep_thread(cep_raw):
    cep = re.sub(r'\D', '', cep_raw)
    if len(cep) != 8:
        app.after(0, lambda: messagebox.showwarning("CEP inválido", "CEP deve ter 8 dígitos."))
        app.after(0, lambda: set_cep_loading(False))
        return

    app.after(0, lambda: set_cep_loading(True))

    url = f"https://viacep.com.br/ws/{cep}/json/"
    try:
        resp = requests.get(url, timeout=6)
        resp.raise_for_status()
        data = resp.json()

        if data.get("erro"):
            app.after(0, lambda: messagebox.showerror("CEP não encontrado", "CEP não foi encontrado."))
            app.after(0, lambda: set_cep_loading(False))
            return

        logradouro = data.get("logradouro", "")
        complemento = data.get("complemento", "")
        bairro = data.get("bairro", "")
        localidade = data.get("localidade", "")
        uf = data.get("uf", "")

        def preencher():
            endereco_entry.delete(0, "end")
            endereco_entry.insert(0, f"{logradouro}".strip())
            complemento_entry.delete(0, "end")
            complemento_entry.insert(0, complemento)
            bairro_entry.delete(0, "end")
            bairro_entry.insert(0, bairro)
            cidade_entry.delete(0, "end")
            cidade_entry.insert(0, localidade)
            uf_entry.delete(0, "end")
            uf_entry.insert(0, uf)
            set_cep_loading(False)

        app.after(0, preencher)

    except requests.RequestException as e:
        app.after(0, lambda: messagebox.showerror("Erro de conexão", f"Não foi possível consultar o CEP:\n{e}"))
        app.after(0, lambda: set_cep_loading(False))

def buscar_cep_event(event=None):
    cep_val = cep_entry.get().strip()
    threading.Thread(target=buscar_cep_thread, args=(cep_val,), daemon=True).start()

def set_cep_loading(loading: bool):
    if loading:
        cep_btn.configure(text="⏳ Buscando...", state="disabled")
        cep_entry.configure(state="disabled")
    else:
        cep_btn.configure(text="🔎 Buscar CEP", state="normal")
        cep_entry.configure(state="normal")

def selecionar_data():
    top = ctk.CTkToplevel(app)
    top.title("Selecionar Data")
    top.geometry("320x320")
    cal = Calendar(top, selectmode="day", date_pattern="dd/mm/yyyy")
    cal.pack(pady=20, fill="both", expand=True)

    def confirmar():
        data_entry.delete(0, "end")
        data_entry.insert(0, cal.get_date())
        top.destroy()

    confirmar_btn = ctk.CTkButton(top, text="Confirmar", command=confirmar, width=120)
    confirmar_btn.pack(pady=10)

def gerar_documento():
    modelo_nome = modelo_combo.get()
    if not modelo_nome or modelo_nome.startswith("Nenhum"):
        messagebox.showwarning("Aviso", "Selecione um modelo de termo.")
        return

    nome_pessoa = nome_entry.get().strip()
    if not nome_pessoa:
        messagebox.showwarning("Aviso", "Digite o nome completo.")
        return

    endereco_full = endereco_entry.get().strip()
    complemento = complemento_entry.get().strip()
    if complemento and complemento not in endereco_full:
        endereco_full = f"{endereco_full} {complemento}".strip()

    valores = {
        "{nome}": nome_pessoa,
        "{cpf}": formatar_cpf(cpf_entry.get()),
        "{rg}": formatar_rg(rg_entry.get()),
        "{endereco}": endereco_full,
        "{bairro}": bairro_entry.get().strip(),
        "{cidade}": cidade_entry.get().strip(),
        "{uf}": uf_entry.get().strip(),
        "{data}": data_entry.get().strip(),
        "{serie}": serie_entry.get().strip(),
    }

    try:
        docs_path = "C:\\Users\\Pichau\\Desktop\\doc-auto\\docs"
        caminho_modelo = os.path.join(docs_path, modelo_nome)
        doc = Document(caminho_modelo)

        for p in doc.paragraphs:
            for ph, val in valores.items():
                if ph in p.text:
                    p.text = p.text.replace(ph, val)

        for t in doc.tables:
            for row in t.rows:
                for cell in row.cells:
                    for ph, val in valores.items():
                        if ph in cell.text:
                            cell.text = cell.text.replace(ph, val)

        nome_formatado = remover_acentos(nome_pessoa).replace(" ", "_") or "Sem_Nome"
        nome_arquivo = f"Termo_{nome_formatado}.docx"
        caminho_padrao = os.path.join(os.path.expanduser("~/Documents"), nome_arquivo)

        salvar_auto = messagebox.askyesno(
            "Salvar documento",
            f"Deseja salvar automaticamente em Documentos como:\n\n{nome_arquivo}\n\nClique 'Não' para escolher pasta."
        )

        if salvar_auto:
            caminho = caminho_padrao
        else:
            caminho = filedialog.asksaveasfilename(defaultextension=".docx", initialfile=nome_arquivo,
                                                   filetypes=[("Documentos Word", "*.docx")])
            if not caminho:
                return

        doc.save(caminho)
        messagebox.showinfo("Sucesso", f"Documento gerado com sucesso em:\n{caminho}")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar documento:\n{e}")

def alternar_tela_cheia():
    global tela_cheia
    tela_cheia = not tela_cheia
    app.attributes("-fullscreen", tela_cheia)
    botao_tela_cheia.configure(text="❌ Sair da Tela Cheia" if tela_cheia else "🖥️ Tela Cheia")

app = ctk.CTk()
app.title("Gerador de Termo Automático - Raphael Vinicius")
app.geometry("920x980")
app.minsize(860, 860)
app.resizable(True, True)

titulo = ctk.CTkLabel(app, text="📄 Gerador de Termo Automático", font=("Arial Rounded MT Bold", 30))
titulo.pack(pady=20)

frame = ctk.CTkScrollableFrame(app, corner_radius=15)
frame.pack(padx=20, pady=10, fill="both", expand=True)

def criar_campo(nome, largura=600):
    lbl = ctk.CTkLabel(frame, text=nome, font=("Arial", 15))
    lbl.pack(pady=(10, 5))
    entrada = ctk.CTkEntry(frame, width=largura, height=40, corner_radius=10)
    entrada.pack()
    return entrada

modelo_label = ctk.CTkLabel(frame, text="Modelo de Termo", font=("Arial", 15))
modelo_label.pack(pady=(10, 5))

docs_path = "C:\\Users\\Pichau\\Desktop\\doc-auto\\docs"
modelos = [f for f in os.listdir(docs_path) if f.endswith(".docx")] if os.path.exists(docs_path) else []
modelo_combo = ctk.CTkOptionMenu(frame, values=modelos or ["Nenhum modelo encontrado"])
modelo_combo.pack(pady=(5, 15))

nome_entry = criar_campo("Nome completo")
cpf_entry = criar_campo("CPF")
rg_entry = criar_campo("RG")

cep_label = ctk.CTkLabel(frame, text="CEP", font=("Arial", 15))
cep_label.pack(pady=(10, 5))
cep_frame = ctk.CTkFrame(frame, fg_color="transparent")
cep_frame.pack(pady=5)
cep_entry = ctk.CTkEntry(cep_frame, width=240, height=40, corner_radius=8)
cep_entry.pack(side="left", padx=(0,10))
cep_entry.bind("<Return>", buscar_cep_event)
cep_entry.bind("<FocusOut>", buscar_cep_event)
cep_entry.bind("<Control-v>", lambda e: app.after(200, buscar_cep_event))  
cep_entry.bind("<Button-2>", lambda e: app.after(200, buscar_cep_event))

cep_btn = ctk.CTkButton(cep_frame, text="🔎 Buscar CEP", width=140, command=buscar_cep_event)
cep_btn.pack(side="left")

endereco_entry = criar_campo("Logradouro (Rua/Av)")
complemento_entry = criar_campo("Complemento (opcional)")
bairro_entry = criar_campo("Bairro")
cidade_entry = criar_campo("Cidade")
uf_entry = criar_campo("UF (Estado)")

data_label = ctk.CTkLabel(frame, text="Data", font=("Arial", 15))
data_label.pack(pady=(10, 5))
data_frame = ctk.CTkFrame(frame, fg_color="transparent")
data_frame.pack(pady=5)
data_entry = ctk.CTkEntry(data_frame, width=300, height=40, corner_radius=10)
data_entry.pack(side="left", padx=10)
data_btn = ctk.CTkButton(data_frame, text="📅 Escolher", width=100, command=selecionar_data)
data_btn.pack(side="left")

serie_entry = criar_campo("Série")

botao_gerar = ctk.CTkButton(app, text="📃 Gerar Documento", command=gerar_documento, width=360, height=60, font=("Arial Rounded MT Bold", 18))
botao_gerar.pack(pady=18)

botao_tela_cheia = ctk.CTkButton(app, text="🖥️ Tela Cheia", width=200, height=40, command=alternar_tela_cheia)
botao_tela_cheia.pack(pady=6)

rodape = ctk.CTkLabel(app, text="Desenvolvido por Raphael Vinicius 💻", font=("Arial", 13), text_color="gray")
rodape.pack(pady=10)

tela_cheia = False
app.mainloop()
