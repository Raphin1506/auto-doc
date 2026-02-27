import os
import json
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog
from tkcalendar import Calendar
# Importando as nossas "caixas de ferramentas" isoladas
from services import CepService
from word_engine import GeradorWord
from utils import formatar_cpf, formatar_rg, remover_acentos
from ai_service import ServicoIA

SETTINGS_FILE = "config.json"

class AutoDocApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configurações da Janela
        self.title("Gerador de Termo Automático - AutoDoc V2")
        self.geometry("920x980")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.pasta_modelos = self.carregar_config()
        self.servico_ia = ServicoIA()
        self.build_ui()

    # ------------------ CONFIGURAÇÕES ------------------
    def carregar_config(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f).get("pasta_modelos", "")
            except:
                return ""
        return ""

    def salvar_config(self, caminho):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump({"pasta_modelos": caminho}, f)
        self.pasta_modelos = caminho

    # ------------------ CONSTRUÇÃO DA TELA ------------------
    def criar_campo(self, frame, nome, largura=600):
        ctk.CTkLabel(frame, text=nome, font=("Arial", 15)).pack(pady=5)
        entry = ctk.CTkEntry(frame, width=largura, height=40)
        entry.pack()
        return entry

    def build_ui(self):
        self.frame = ctk.CTkScrollableFrame(self)
        self.frame.pack(padx=20, pady=10, fill="both", expand=True)

        # --- ÁREA MÁGICA DA IA ---
        ctk.CTkLabel(self.frame, text="🤖 Cole o texto do chamado aqui:", font=("Arial", 15, "bold"), text_color="#00ffcc").pack(pady=(10, 0))
        self.texto_ia = ctk.CTkTextbox(self.frame, width=600, height=80)
        self.texto_ia.pack(pady=5)
        
        ctk.CTkButton(self.frame, text="✨ Analisar com IA", command=self.analisar_chamado_ia, fg_color="#2b8a3e", hover_color="#237032").pack(pady=(0, 15))
        
        # Linha separadora
        ctk.CTkFrame(self.frame, width=600, height=2, fg_color="gray").pack(pady=10)
        # -------------------------

        ctk.CTkButton(self.frame, text="📂 Selecionar Pasta de Modelos", command=self.selecionar_pasta_modelos).pack(pady=10)

        ctk.CTkLabel(self.frame, text="Modelo de Termo", font=("Arial", 15)).pack()
        self.modelo_combo = ctk.CTkOptionMenu(self.frame, values=["Nenhum modelo encontrado"])
        self.modelo_combo.pack(pady=10)
        
        if self.pasta_modelos:
            self.atualizar_modelos(self.pasta_modelos)

        self.nome_entry = self.criar_campo(self.frame, "Nome completo")
        self.cpf_entry = self.criar_campo(self.frame, "CPF")
        self.rg_entry = self.criar_campo(self.frame, "RG")

        # Sessão CEP
        ctk.CTkLabel(self.frame, text="CEP").pack()
        self.cep_entry = ctk.CTkEntry(self.frame, width=200)
        self.cep_entry.pack()
        self.cep_entry.bind("<Return>", self.buscar_cep_event)
        
        self.cep_btn = ctk.CTkButton(self.frame, text="🔎 Buscar CEP", command=self.buscar_cep_event)
        self.cep_btn.pack(pady=5)

        self.endereco_entry = self.criar_campo(self.frame, "Logradouro")
        self.complemento_entry = self.criar_campo(self.frame, "Complemento")
        self.bairro_entry = self.criar_campo(self.frame, "Bairro")
        self.cidade_entry = self.criar_campo(self.frame, "Cidade")
        self.uf_entry = self.criar_campo(self.frame, "UF")

        self.data_entry = self.criar_campo(self.frame, "Data")
        ctk.CTkButton(self.frame, text="📅 Escolher Data", command=self.selecionar_data).pack(pady=5)

        self.serie_entry = self.criar_campo(self.frame, "Série")

        ctk.CTkButton(self, text="📃 Gerar Documento", command=self.gerar_documento, width=260, height=50).pack(pady=15)

    # ------------------ LÓGICA DE INTERAÇÃO ------------------
    def atualizar_modelos(self, pasta):
        if not os.path.exists(pasta):
            self.modelo_combo.configure(values=["Nenhum modelo encontrado"])
            self.modelo_combo.set("Nenhum modelo encontrado")
            return
        modelos = [f for f in os.listdir(pasta) if f.endswith(".docx") and not f.startswith("~")]
        if not modelos:
            modelos = ["Nenhum modelo encontrado"]
        self.modelo_combo.configure(values=modelos)
        self.modelo_combo.set(modelos[0])

    def selecionar_pasta_modelos(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta dos modelos")
        if pasta:
            self.salvar_config(pasta)
            self.atualizar_modelos(pasta)
            messagebox.showinfo("Sucesso", "Pasta definida com sucesso!")

    def buscar_cep_event(self, event=None):
        cep_raw = self.cep_entry.get().strip()
        self.cep_btn.configure(text="⏳ Buscando...", state="disabled")
        threading.Thread(target=self.buscar_cep_thread, args=(cep_raw,), daemon=True).start()

    def buscar_cep_thread(self, cep_raw):
        try:
            # Chama o nosso arquivo services.py (que não sabe nada de tela)
            dados_cep = CepService.buscar_cep(cep_raw)
            # Usa o after para devolver os dados pra tela com segurança
            self.after(0, lambda: self.preencher_cep(dados_cep))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erro", str(e)))
        finally:
            self.after(0, lambda: self.cep_btn.configure(text="🔎 Buscar CEP", state="normal"))

    def preencher_cep(self, dados):
        self.endereco_entry.delete(0, "end")
        self.endereco_entry.insert(0, dados["logradouro"])
        self.bairro_entry.delete(0, "end")
        self.bairro_entry.insert(0, dados["bairro"])
        self.cidade_entry.delete(0, "end")
        self.cidade_entry.insert(0, dados["cidade"])
        self.uf_entry.delete(0, "end")
        self.uf_entry.insert(0, dados["uf"])

    def selecionar_data(self):
        top = ctk.CTkToplevel(self)
        top.title("Selecionar Data")
        top.geometry("320x320")
        cal = Calendar(top, selectmode="day", date_pattern="dd/mm/yyyy")
        cal.pack(pady=20, expand=True, fill="both")
        
        def confirmar():
            self.data_entry.delete(0, "end")
            self.data_entry.insert(0, cal.get_date())
            top.destroy()
            
        ctk.CTkButton(top, text="Confirmar", command=confirmar).pack(pady=10)
    # ------------------ ANÁLISE DE CHAMADO DA IA ------------------  
    
    def analisar_chamado_ia(self):
        texto_baguncado = self.texto_ia.get("1.0", "end-1c").strip()
        
        if not texto_baguncado:
            messagebox.showwarning("Aviso", "Cole algum texto para a IA analisar.")
            return
            
        # Chama o serviço híbrido (spaCy + RegEx)
        dados_ia = self.servico_ia.analisar_texto(texto_baguncado)
        
        # Preenche os campos automaticamente se a IA achou alguma coisa
        def preencher_campo(entry, valor):
            if valor:
                entry.delete(0, "end")
                entry.insert(0, valor)

        preencher_campo(self.nome_entry, dados_ia["nome"])
        preencher_campo(self.cpf_entry, dados_ia["cpf"])
        preencher_campo(self.rg_entry, dados_ia["rg"])
        preencher_campo(self.cep_entry, dados_ia["cep"])
        preencher_campo(self.data_entry, dados_ia["data"])
        preencher_campo(self.serie_entry, dados_ia["serie"])
        
        # Se achou CEP, já manda buscar o endereço automaticamente!
        if dados_ia["cep"]:
            self.buscar_cep_event()
            
        messagebox.showinfo("IA Concluída", "Campos preenchidos com o que foi encontrado!")
    
    # ------------------ O CORAÇÃO: GERAR DOCUMENTO ------------------
    def gerar_documento(self):
        if not self.pasta_modelos or not os.path.exists(self.pasta_modelos):
            messagebox.showerror("Erro", "Nenhuma pasta de modelos configurada!")
            return

        modelo_nome = self.modelo_combo.get()
        caminho_modelo = os.path.join(self.pasta_modelos, modelo_nome)
        nome_pessoa = self.nome_entry.get().strip()

        if not nome_pessoa:
            messagebox.showwarning("Aviso", "Digite o nome completo.")
            return

        # Empacota tudo bonitinho usando nossas funções do utils.py
        dados = {
            "nome": nome_pessoa,
            "cpf": formatar_cpf(self.cpf_entry.get()),
            "rg": formatar_rg(self.rg_entry.get()),
            "endereco": self.endereco_entry.get(),
            "complemento": self.complemento_entry.get(),
            "bairro": self.bairro_entry.get(),
            "cidade": self.cidade_entry.get(),
            "uf": self.uf_entry.get(),
            "data": self.data_entry.get(),
            "serie": self.serie_entry.get(),
        }

        nome_formatado = remover_acentos(nome_pessoa).replace(" ", "_")
        caminho_salvar = filedialog.asksaveasfilename(
            defaultextension=".docx",
            initialfile=f"Termo_{nome_formatado}.docx",
            filetypes=[("Documentos Word", "*.docx")]
        )

        if caminho_salvar:
            try:
                # Passa a bola pro word_engine.py resolver
                GeradorWord.criar_termo(caminho_modelo, caminho_salvar, dados)
                messagebox.showinfo("Sucesso", "Documento gerado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro Crítico", str(e))