import customtkinter as ctk
from tkinter import messagebox, filedialog
from tkcalendar import Calendar
from docx import Document
import re
import os
import sys
import requests
import threading
import unicodedata

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


# ---------- FUNÇÕES AUXILIARES ---------- #

def resource_path(relative_path):
    """
    Função para acessar arquivos quando convertido em .exe
    """
    try:
        base_path = sys._MEIPASS  
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def remover_acentos(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def formatar_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)[:11]
    return re.sub(r'(\d{3})(\d{3})(\d{3})(\d{0,2})', r'\1.\2.\3-\4', cpf)


def formatar_rg(rg):
    rg = re.sub(r'\D', '', rg)[:9]
    return re.sub(r'(\d{2})(\d{3})(\d{3})(\d{0,1})', r'\1.\2.\3-\4', rg)


# ---------- CEP (THREAD) ---------- #

def buscar_cep_thread(cep_raw):
    cep = re.sub(r'\D', '', cep_raw)
    if len(cep) != 8:
        app.after(0, lambda: messagebox.showwarning("CEP inválido", "CEP deve ter 8 dígitos."))
        app.after(0, lambda: set_cep_loading(False))
        return

    app.after(0, lambda: set_cep_loading(True))

    try:
        resp = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=6)
        resp.raise_for_status()
        data = resp.json()

        if data.get("erro"):
            app.after(0, lambda: messagebox.showerror("CEP não encontrado", "CEP não foi encontrado."))
            app.after(0, lambda: set_cep_loading(False))
            return

        def preencher():
            endereco_entry.delete(0, "end")
            endereco_entry.insert(0, data.get("logradouro", ""))
            complemento_entry.delete(0, "end")
            complemento_entry.insert(0, data.get("complemento", ""))
            bairro_entry.delete(0, "end")
            bairro_entry.insert(0, data.get("bairro", ""))
            cidade_entry.delete(0, "end")
            cidade_entry.insert(0, data.get("localidade", ""))
            uf_entry.delete(0, "end")
            uf_entry.insert(0, data.get("uf", ""))
            set_cep_loading(False)

        app.after(0, preencher)

    except Exception as e:
        app.after(0, lambda: messagebox.showerror("Erro", f"Erro ao consultar CEP:\n{e}"))
        app.after(0, lambda: set_cep_loading(False))


def buscar_cep_event(event=None):
    threading.Thread(target=buscar_cep_thread, args=(cep_entry.get().strip(),), daemon=True).start()


def set_cep_loading(loading: bool):
    cep_btn.configure(text="⏳ Buscando..." if loading else "🔎 Buscar CEP",
                      state="disabled" if loading else "normal")
    cep_entry.configure(state="disabled" if loading else "normal")


# ---------- SELEÇÃO DE DATA ---------- #

def selecionar_data():
    top = ctk.CTkToplevel(app)
    top.title("Selecionar Data")
    top.geometry("320x320")

    cal = Calendar(top, selectmode="day", date_pattern="dd/mm/yyyy")
    cal.pack(pady=20, expand=True, fill="both")

    ctk.CTkButton(top, text="Confirmar",
                  command=lambda: (data_entry.delete(0, "end"),
                                   data_entry.insert(0, cal.get_date()),
                                   top.destroy())).pack(pady=10)


# ---------- GERAR DOCUMENTO ---------- #

def gerar_documento():
    modelo_nome = modelo_combo.get()

    if not modelo_nome or modelo_nome.startswith("Nenhum"):
        messagebox.showwarning("Aviso", "Selecione um modelo de termo.")
        return

    nome_pessoa = nome_entry.get().strip()
    if not nome_pessoa:
        messagebox.showwarning("Aviso", "Digite o nome completo.")
        return
    docs_path = resource_path("doc")

    caminho_modelo = os.path.join(docs_path, modelo_nome)

    try:
        doc = Document(caminho_modelo)

        valores = {
            "{nome}": nome_pessoa,
            "{cpf}": formatar_cpf(cpf_entry.get()),
            "{rg}": formatar_rg(rg_entry.get()),
            "{endereco}": endereco_entry.get(),
            "{bairro}": bairro_entry.get(),
            "{cidade}": cidade_entry.get(),
            "{uf}": uf_entry.get(),
            "{data}": data_entry.get(),
            "{serie}": serie_entry.get(),
        }

        for p in doc.paragraphs:
            for ph, val in valores.items():
                p.text = p.text.replace(ph, val)

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for ph, val in valores.items():
                        cell.text = cell.text.replace(ph, val)

        nome_formatado = remover_acentos(nome_pessoa).replace(" ", "_")
        nome_arquivo = f"Termo_{nome_formatado}.docx"
        caminho_salvar = filedialog.asksaveasfilename(defaultextension=".docx",
                                                      initialfile=nome_arquivo,
                                                      filetypes=[("Word Document", "*.docx")])

        if caminho_salvar:
            doc.save(caminho_salvar)
            messagebox.showinfo("Sucesso", "Documento gerado com sucesso!")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar documento:\n{e}")


# ---------- INTERFACE ---------- #

app = ctk.CTk()
app.title("Gerador de Termo Automático - Raphael Vinicius")


try:
    app.iconbitmap(resource_path("icon.ico"))
except:
    pass

app.geometry("920x980")
app.minsize(860, 860)

frame = ctk.CTkScrollableFrame(app, corner_radius=15)
frame.pack(padx=20, pady=10, fill="both", expand=True)


def criar_campo(nome, largura=600):
    ctk.CTkLabel(frame, text=nome, font=("Arial", 15)).pack(pady=(10, 5))
    entry = ctk.CTkEntry(frame, width=largura, height=40)
    entry.pack()
    return entry

docs_path = resource_path("doc")
modelos = [f for f in os.listdir(docs_path) if f.endswith(".docx")] if os.path.exists(docs_path) else ["Nenhum modelo encontrado"]

ctk.CTkLabel(frame, text="Modelo de Termo", font=("Arial", 15)).pack(pady=(10, 5))
modelo_combo = ctk.CTkOptionMenu(frame, values=modelos)
modelo_combo.pack(pady=10)

nome_entry = criar_campo("Nome completo")
cpf_entry = criar_campo("CPF")
rg_entry = criar_campo("RG")

ctk.CTkLabel(frame, text="CEP").pack()
cep_entry = ctk.CTkEntry(frame, width=200)
cep_entry.pack()
cep_entry.bind("<Return>", buscar_cep_event)

cep_btn = ctk.CTkButton(frame, text="🔎 Buscar CEP", command=buscar_cep_event)
cep_btn.pack(pady=5)

endereco_entry = criar_campo("Logradouro")
complemento_entry = criar_campo("Complemento (opcional)")
bairro_entry = criar_campo("Bairro")
cidade_entry = criar_campo("Cidade")
uf_entry = criar_campo("UF")

data_entry = criar_campo("Data")
ctk.CTkButton(frame, text="📅 Escolher Data", command=selecionar_data).pack(pady=5)

serie_entry = criar_campo("Série")

ctk.CTkButton(app, text="📃 Gerar Documento", command=gerar_documento, width=260, height=50).pack(pady=15)

app.mainloop()
