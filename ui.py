import os
import json
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog
from tkcalendar import Calendar

# Importando as suas classes e serviços
from services import CepService
from word_engine import GeradorWord
from utils import formatar_cpf, formatar_rg, remover_acentos
from ai_service import ServicoIA

SETTINGS_FILE = "config.json"

class AutoDocApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configurações da Janela
        self.title("Gerador de Termo - AutoDoc V2.1 (Dinâmico)")
        self.geometry("1100x800")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Carrega a pasta salva no config.json (Herança da sua V2!)
        self.pasta_modelos = self.carregar_config()
        
        # Instancia os motores
        self.gerador_word = GeradorWord()
        self.servico_ia = ServicoIA()
        
        # Dicionário vivo para os campos gerados dinamicamente
        self.campos_dinamicos = {}

        self.build_ui()
        
        # Tenta carregar a IA padrão ao iniciar
        self.servico_ia.carregar_modelo("modelo_autodoc")

    # ------------------ CONFIGURAÇÕES (Seu código legado salvo!) ------------------
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
    def build_ui(self):
        # --- FRAME ESQUERDO (Controles e IA) ---
        self.frame_esq = ctk.CTkFrame(self, width=380)
        self.frame_esq.pack(side="left", fill="y", padx=20, pady=20)

        ctk.CTkLabel(self.frame_esq, text="⚙️ Painel de Controle", font=("Arial", 20, "bold")).pack(pady=10)

        # 1. Pasta de Modelos
        ctk.CTkButton(self.frame_esq, text="📂 Selecionar Pasta de Modelos", command=self.selecionar_pasta_modelos, fg_color="gray").pack(fill="x", padx=10, pady=(10, 20))

        # 2. Seletor de Cérebro (IA Multi-Domínio)
        ctk.CTkLabel(self.frame_esq, text="1. Escolha a I.A. (Departamento):").pack(anchor="w", padx=10)
        self.combo_ia = ctk.CTkOptionMenu(
            self.frame_esq, 
            values=["modelo_autodoc", "modelo_rh", "modelo_juridico"], 
            command=self.trocar_cerebro_ia
        )
        self.combo_ia.pack(fill="x", padx=10, pady=5)

        # 3. Seletor de Modelo (Word)
        ctk.CTkLabel(self.frame_esq, text="2. Escolha o Modelo Word:").pack(anchor="w", padx=10, pady=(10, 0))
        self.combo_modelos = ctk.CTkOptionMenu(
            self.frame_esq, 
            values=["Nenhum modelo encontrado"],
            command=self.desenhar_campos_dinamicos
        )
        self.combo_modelos.pack(fill="x", padx=10, pady=5)

        # 4. O Campo Mágico
        ctk.CTkLabel(self.frame_esq, text="3. Campo Mágico (Cole o chamado):", text_color="#00ffcc", font=("Arial", 13, "bold")).pack(anchor="w", padx=10, pady=(20, 0))
        self.texto_magico = ctk.CTkTextbox(self.frame_esq, height=120)
        self.texto_magico.pack(fill="x", padx=10, pady=5)

        self.btn_analisar = ctk.CTkButton(self.frame_esq, text="✨ Analisar com IA", fg_color="#2b8a3e", hover_color="#237032", command=self.analisar_com_ia)
        self.btn_analisar.pack(fill="x", padx=10, pady=10)

        self.btn_gerar = ctk.CTkButton(self.frame_esq, text="📄 Gerar Documento", fg_color="#275dad", hover_color="#1c4585", height=45, command=self.gerar_documento)
        self.btn_gerar.pack(fill="x", padx=10, side="bottom", pady=20)

        # --- FRAME DIREITO (O Formulário Dinâmico) ---
        self.frame_dir = ctk.CTkScrollableFrame(self)
        self.frame_dir.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(self.frame_dir, text="📝 Formulário Dinâmico", font=("Arial", 20, "bold")).pack(pady=10)
        
        # Container vazio onde a mágica acontece
        self.container_campos = ctk.CTkFrame(self.frame_dir, fg_color="transparent")
        self.container_campos.pack(fill="both", expand=True)
        
        # --- BOTÃO SOBRE (No final do frame esquerdo) ---
        self.btn_sobre = ctk.CTkButton(
            self.frame_esq, 
            text="ℹ️ Sobre o App", 
            fg_color="transparent", 
            text_color="gray", 
            hover_color="#333",
            width=100,
            command=self.exibir_sobre
        )
        self.btn_sobre.pack(side="bottom", pady=10) # Fica fixo lá embaixo no painel

        # ========================================================
        # O GATILHO FINAL: Só chama os modelos depois da tela existir!
        # ========================================================
        if self.pasta_modelos:
            self.atualizar_modelos(self.pasta_modelos)
                  

    # ------------------ LÓGICA DE INTERAÇÃO ------------------
    def atualizar_modelos(self, pasta):
        if not os.path.exists(pasta):
            return
        modelos = [f for f in os.listdir(pasta) if f.endswith(".docx") and not f.startswith("~")]
        if modelos:
            self.combo_modelos.configure(values=modelos)
            self.combo_modelos.set(modelos[0])
            self.desenhar_campos_dinamicos(modelos[0]) # Já desenha a tela pro primeiro modelo!

    def selecionar_pasta_modelos(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta dos modelos")
        if pasta:
            self.salvar_config(pasta)
            self.atualizar_modelos(pasta)
            messagebox.showinfo("Sucesso", "Pasta atualizada! Modelos carregados.")

    def trocar_cerebro_ia(self, escolha):
        sucesso = self.servico_ia.carregar_modelo(escolha)
        if not sucesso:
            messagebox.showwarning("Aviso", f"A pasta '{escolha}' não existe ainda. Treine a IA primeiro!")

    def desenhar_campos_dinamicos(self, nome_arquivo_word):
        # 1. Limpa o container
        for widget in self.container_campos.winfo_children():
            widget.destroy()
        self.campos_dinamicos.clear()
        
        if not self.pasta_modelos: return
        
        caminho_completo = os.path.join(self.pasta_modelos, nome_arquivo_word)
        try:
            tags = self.gerador_word.mapear_variaveis(caminho_completo)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível ler o modelo: {e}")
            return

        # 2. Desenha os campos baseados no Word
        for tag in tags:
            label_texto = tag.replace("_", " ").title()
            ctk.CTkLabel(self.container_campos, text=f"{label_texto}:", font=("Arial", 14, "bold")).pack(anchor="w", pady=(15, 0), padx=10)
            
            entrada = ctk.CTkEntry(self.container_campos, width=450, height=35)
            entrada.pack(anchor="w", pady=(0, 5), padx=10)
            
            self.campos_dinamicos[tag] = entrada

            # --- GATILHOS INTELIGENTES ---
            # Se for CEP, liga a API
            if tag.lower() == "cep":
                entrada.bind("<Return>", self.buscar_cep_event)
                ctk.CTkLabel(self.container_campos, text="↳ Pressione ENTER para buscar endereço", font=("Arial", 11, "italic"), text_color="#a8a8a8").pack(anchor="w", padx=10)
            
            # Se for DATA, avisa que o formato é manual por enquanto (poderíamos plugar o calendário aqui depois)
            if "data" in tag.lower():
                ctk.CTkLabel(self.container_campos, text="↳ Digite no formato DD/MM/AAAA ou escolha a data pelo calendário", font=("Arial", 11, "italic"), text_color="#a8a8a8").pack(anchor="w", padx=10)
                
                # 2. Criar um Frame para deixar o Entry e o Botão lado a lado
                frame_data = ctk.CTkEntry(self.container_campos, fg_color="transparent")
                frame_data.pack(anchor="w", padx=(0, 10))
                
                # 3. Campo de entrada da data
                entry_data = ctk.CTkEntry(frame_data, placeholder_text="DD/MM/AAAA", width=150)
                entry_data.pack(side="left", padx=(0, 10))
                
                def abrir_calendario():
                    # Cria uma janela secundária (pop-up)
                    janela_calendario = ctk.CTkToplevel()
                    janela_calendario.title("Escolha uma Data")
                    janela_calendario.geometry("300x250")
                    janela_calendario.grab_set()
                    
                    cal = Calendar(janela_calendario, selectmode='day', date_pattern='dd/mm/yyyy')
                    cal.pack(padx=20, pady=15, fill="both", expand=True)

                    # Função para capturar a data escolhida e colocar no Entry
                    def confirmar_data():
                        data_escolhida = cal.get_date()
                        entry_data.delete(0, "end") # Limpa o que estiver no campo
                        entry_data.insert(0, data_escolhida) # Insere a nova data
                        janela_calendario.destroy() # Fecha o pop-up

                    # Botão para confirmar a escolha dentro do pop-up
                    btn_confirmar = ctk.CTkButton(janela_calendario, text="Confirmar Data", command=confirmar_data)
                    btn_confirmar.pack(pady=(0, 15))

                # 5. Botão que fica ao lado do campo de texto para abrir o calendário
                btn_calendario = ctk.CTkButton(
                    frame_data, 
                    text="📅 Abrir Calendário", 
                    width=120, 
                    command=abrir_calendario
                )
                btn_calendario.pack(side="left")

    # ------------------ API DE CEP DINÂMICA ------------------
    def buscar_cep_event(self, event=None):
        if "cep" in self.campos_dinamicos:
            cep_raw = self.campos_dinamicos["cep"].get().strip()
            if cep_raw:
                threading.Thread(target=self.buscar_cep_thread, args=(cep_raw,), daemon=True).start()

    def buscar_cep_thread(self, cep_raw):
        try:
            dados_cep = CepService.buscar_cep(cep_raw)
            self.after(0, lambda: self.preencher_cep(dados_cep))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erro CEP", str(e)))

    def preencher_cep(self, dados):
        mapa_campos = {
            "endereco": dados["logradouro"],
            "logradouro": dados["logradouro"],
            "bairro": dados["bairro"],
            "cidade": dados["cidade"],
            "uf": dados["uf"]
        }
        for tag_word, valor_api in mapa_campos.items():
            if tag_word in self.campos_dinamicos:
                widget = self.campos_dinamicos[tag_word]
                widget.delete(0, "end")
                widget.insert(0, valor_api)

    # ------------------ ANÁLISE IA ------------------
    def analisar_com_ia(self):
        texto = self.texto_magico.get("1.0", "end").strip()
        if not texto:
            messagebox.showwarning("Aviso", "Cole o chamado primeiro!")
            return

        dados_extraidos = self.servico_ia.analisar_texto(texto)

        for tag, widget_entrada in self.campos_dinamicos.items():
            # A IA procura por 'cpf', 'nome', 'rg', etc.
            if tag.lower() in dados_extraidos and dados_extraidos[tag.lower()]:
                widget_entrada.delete(0, "end")
                widget_entrada.insert(0, dados_extraidos[tag.lower()])
        
        # Dispara o CEP automaticamente se a IA achou um
        if dados_extraidos.get("cep") and "cep" in self.campos_dinamicos:
            self.buscar_cep_event()
            
        messagebox.showinfo("Sucesso", "IA preencheu o que encontrou!")

    # ------------------ GERAR DOCUMENTO ------------------
    def gerar_documento(self):
        modelo_nome = self.combo_modelos.get()
        if not modelo_nome or modelo_nome == "Nenhum modelo encontrado":
            messagebox.showerror("Erro", "Selecione um modelo válido.")
            return

        dados_finais = {}
        for tag, widget_entrada in self.campos_dinamicos.items():
            valor = widget_entrada.get().strip()
            # Aplica formatações mágicas na saída se necessário
            if tag.lower() == "cpf": valor = formatar_cpf(valor)
            if tag.lower() == "rg": valor = formatar_rg(valor)
            
            dados_finais[tag] = valor

        caminho_modelo = os.path.join(self.pasta_modelos, modelo_nome)
        
        nome_sugerido = dados_finais.get("nome", "Documento_Gerado")
        nome_formatado = remover_acentos(nome_sugerido).replace(" ", "_")
        
        caminho_salvar = filedialog.asksaveasfilename(
            defaultextension=".docx",
            initialfile=f"Termo_{nome_formatado}.docx",
            filetypes=[("Word", "*.docx")]
        )

        if caminho_salvar:
            try:
                # Aqui o word_engine faz o trabalho dele
                GeradorWord.criar_termo(caminho_modelo, caminho_salvar, dados_finais)
                messagebox.showinfo("Sucesso", "Documento salvo com perfeição!")
            except Exception as e:
                messagebox.showerror("Erro Crítico", str(e))
                
    def exibir_sobre(self):
        msg = (
            "🚀 AutoDoc V2.1 (Dinâmico)\n"
            "----------------------------------------\n"
            "Desenvolvido por: Raphael Vinícius Amaral de Andrade\n\n"
            "Este aplicativo utiliza Inteligência Artificial e varredura \n"
            "dinâmica via Regex para automatizar a criação de termos \n"
            "e documentos Word com precisão cirúrgica.\n\n"
            "Versão: 2.1 (Edição 'O Retorno do Regex')"
        )
        messagebox.showinfo("Sobre o App", msg)