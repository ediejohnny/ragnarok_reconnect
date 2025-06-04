#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import os
import logging
from logging.handlers import RotatingFileHandler
from PIL import Image, ImageTk
import queue

# Importa as funções do sistema
from funcoes import (
    verificar_desconexao,
    iniciar_processo_login_completo,
    clicar_para_focar_jogo,
    set_gui_logger
)

class RagnarokReconnectGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ragnarok Reconnect - Sistema de Reconexão Automática")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variáveis de controle
        self.is_running = False
        self.monitor_thread = None
        self.log_queue = queue.Queue()
        
        # Configurar sistema de logs
        self.setup_logging()
        
        # Configurar estilo
        self.setup_style()
        
        # Criar interface
        self.create_widgets()
        
        # Inicializar Interception
        self.init_interception()
        
        # Monitorar logs
        self.check_log_queue()
        
        # Protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_logging(self):
        """Configura o sistema de logs com rotação de arquivos"""
        # Criar diretório se não existir
        log_dir = r"C:\Reconnect"
        os.makedirs(log_dir, exist_ok=True)
        
        # Nome do arquivo com timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"log_{timestamp}.txt")
        
        # Configurar logging com rotação (10MB)
        self.logger = logging.getLogger("RagnarokReconnect")
        self.logger.setLevel(logging.INFO)
        
        # Remover handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Handler rotativo para arquivo
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Configurar o logger do funcoes.py para usar o mesmo sistema
        set_gui_logger(self.logger)
        
        self.log_info("Sistema de logs inicializado")
        self.log_info(f"Logs salvos em: {log_dir}")

    def setup_style(self):
        """Configura o estilo da interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores modernas
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'), foreground='#34495e')
        style.configure('Info.TLabel', font=('Segoe UI', 9), foreground='#7f8c8d')
        style.configure('Start.TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('Stop.TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('Install.TButton', font=('Segoe UI', 10, 'bold'))

    def create_widgets(self):
        """Cria todos os widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # === LADO ESQUERDO: IMAGEM ===
        self.create_image_section(main_frame)
        
        # === LADO DIREITO: CONTROLES ===
        self.create_controls_section(main_frame)
        
        # === PARTE INFERIOR: LOGS ===
        self.create_log_section(main_frame)

    def create_image_section(self, parent):
        """Cria a seção da imagem (lado esquerdo)"""
        image_frame = ttk.LabelFrame(parent, text="Sistema", padding="10")
        image_frame.grid(row=0, column=0, rowspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        try:
            # Carregar e redimensionar imagem avatar_pin.png
            if os.path.exists("avatar_pin.png"):
                image = Image.open("avatar_pin.png")
                # Redimensionar mantendo proporção
                image.thumbnail((200, 300), Image.Resampling.LANCZOS)
                self.avatar_image = ImageTk.PhotoImage(image)
                
                avatar_label = ttk.Label(image_frame, image=self.avatar_image)
                avatar_label.grid(row=0, column=0, pady=10)
            else:
                # Placeholder se imagem não existir
                placeholder = ttk.Label(image_frame, text="Avatar PIN\n(Imagem não encontrada)", 
                                      justify=tk.CENTER, font=('Segoe UI', 10))
                placeholder.grid(row=0, column=0, pady=10)
        except Exception as e:
            self.log_error(f"Erro ao carregar avatar_pin.png: {e}")
            placeholder = ttk.Label(image_frame, text="Avatar PIN\n(Erro ao carregar)", 
                                  justify=tk.CENTER, font=('Segoe UI', 10))
            placeholder.grid(row=0, column=0, pady=10)
        
        # Status do sistema
        self.status_label = ttk.Label(image_frame, text="Sistema Parado", 
                                    style='Header.TLabel', foreground='red')
        self.status_label.grid(row=1, column=0, pady=10)

    def create_controls_section(self, parent):
        """Cria a seção de controles (lado direito)"""
        controls_frame = ttk.LabelFrame(parent, text="Configurações", padding="10")
        controls_frame.grid(row=0, column=1, rowspan=3, sticky=(tk.W, tk.E, tk.N), padx=(10, 0))
        controls_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(controls_frame, text="Reconexão Automática", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Campo Senha
        ttk.Label(controls_frame, text="Senha:", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.senha_var = tk.StringVar(value="senha123")
        self.senha_entry = ttk.Entry(controls_frame, textvariable=self.senha_var, show="*", width=30)
        self.senha_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Campo PIN
        ttk.Label(controls_frame, text="PIN:", style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.pin_var = tk.StringVar(value="1234")
        self.pin_entry = ttk.Entry(controls_frame, textvariable=self.pin_var, width=30)
        self.pin_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Validação do PIN
        self.pin_entry.bind('<KeyRelease>', self.validate_pin)
        
        # Botões
        button_frame = ttk.Frame(controls_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="🚀 Iniciar Sistema", 
                                     command=self.start_system, style='Start.TButton')
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Parar Sistema", 
                                    command=self.stop_system, style='Stop.TButton', state='disabled')
        
        self.install_button = ttk.Button(button_frame, text="⚙️ Instalar Drivers", 
                                    command=self.install_drivers, style='Install.TButton')
        
        self.install_button.grid(row=0, column=2, padx=5)
        
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Informações do sistema
        info_frame = ttk.Frame(controls_frame)
        info_frame.grid(row=4, column=0, columnspan=2, pady=20, sticky=(tk.W, tk.E))
        
        ttk.Label(info_frame, text="ℹ️ Informações:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        info_text = ("• O sistema monitora desconexões automaticamente\n"
                    "• Logs são salvos em C:\\Reconnect\\\n"
                    "• Arquivos de log rotacionam a cada 10MB\n"
                    "• Certifique-se de voltar para o jogo após clicar em Iniciar Sistema")
        
        ttk.Label(info_frame, text=info_text, style='Info.TLabel', justify=tk.LEFT).grid(row=1, column=0, sticky=tk.W)

    def create_log_section(self, parent):
        """Cria a seção de logs (parte inferior)"""
        log_frame = ttk.LabelFrame(parent, text="Logs do Sistema", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Área de texto para logs
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, state='disabled',
                                                font=('Consolas', 9), wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Botão para limpar logs
        clear_button = ttk.Button(log_frame, text="🗑️ Limpar Logs", command=self.clear_logs)
        clear_button.grid(row=1, column=0, pady=(5, 0))

    def init_interception(self):
        """Inicializa o Interception"""
        try:
            import interception
            self.log_info("Inicializando Interception para automação precisa...")
            interception.auto_capture_devices(keyboard=True, mouse=True)
            self.log_info("✅ Interception inicializado com sucesso!")
        except ImportError:
            self.log_warning("⚠️ Interception não disponível. Usando PyAutoGUI como fallback.")
        except Exception as e:
            self.log_error(f"❌ Erro ao inicializar Interception: {e}")

    def validate_pin(self, event=None):
        """Valida o PIN digitado"""
        pin = self.pin_var.get()
        if pin and not pin.isdigit():
            # Remove caracteres não numéricos
            cleaned_pin = ''.join(c for c in pin if c.isdigit())
            self.pin_var.set(cleaned_pin)

    def start_system(self):
        """Inicia o sistema de monitoramento"""
        # Validar campos
        senha = self.senha_var.get().strip()
        pin = self.pin_var.get().strip()
        
        if not senha:
            messagebox.showerror("Erro", "Por favor, insira a senha.")
            return
        
        if not pin or len(pin) != 4:
            messagebox.showerror("Erro", "Por favor, insira um PIN de 4 dígitos.")
            return
        
        # Verificar imagens necessárias
        required_images = ['desconectado.png', 'avatar_pin.png', 'confirmar.png', 'jogar.png']
        missing_images = [img for img in required_images if not os.path.exists(img)]
        
        if missing_images:
            missing_list = '\n• '.join(missing_images)
            result = messagebox.askywarning(
                "Imagens não encontradas", 
                f"As seguintes imagens não foram encontradas:\n• {missing_list}\n\nO sistema pode não funcionar corretamente. Continuar mesmo assim?"
            )
            if not result:
                return
        
        # Iniciar sistema
        self.is_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_label.config(text="Sistema Ativo", foreground='green')
        
        # Iniciar thread de monitoramento
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.log_info("🚀 Sistema iniciado com sucesso!")
        self.log_info(f"👤 Usuário: {'*' * len(senha)}")
        self.log_info(f"🔢 PIN: {'*' * len(pin)}")

    def stop_system(self):
        """Para o sistema de monitoramento"""
        self.is_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='normal')
        self.status_label.config(text="Sistema Parado", foreground='red')
        
        self.log_info("⏹️ Sistema parado pelo usuário")
        
    def install_drivers(self):
        """Alerta que a instalação de drivers ainda não está implementada"""
        messagebox.showinfo("Atenção", "Não implementado ainda")

    def monitor_loop(self):
        """Loop principal de monitoramento (executa em thread separada)"""
        self.log_info("🔍 Iniciando monitoramento de desconexão...")
        
        while self.is_running:
            try:
                # Verificar desconexão
                if verificar_desconexao(image_path='desconectado.png', confidence=0.9):
                    self.log_info("🔌 Desconexão detectada! Iniciando processo de reconexão...")
                    
                    # Tentar focar no jogo
                    if not clicar_para_focar_jogo(imagem_alvo_foco='ragnarok.png', confianca_imagem=0.8):
                        self.log_error("❌ Falha ao focar no jogo. Tentando novamente em 20s...")
                        time.sleep(20)
                        continue
                    
                    # Executar processo de login
                    senha = self.senha_var.get()
                    pin = self.pin_var.get()
                    
                    login_sucesso = iniciar_processo_login_completo(
                        senha=senha,
                        pin=pin,
                        pasta_imagens_pin="",
                        image_confirm='confirmar.png',
                        image_senha_screen='senha.png',
                        image_name='jogar.png',
                        image_ragnarok_focus='ragnarok.png',
                        image_jogar='jogar.png',
                        confianca_geral=0.8,
                        confianca_foco=0.8
                    )
                    
                    if login_sucesso:
                        self.log_info("✅ Reconexão realizada com sucesso!")
                    else:
                        self.log_error("❌ Falha na reconexão. Tentando novamente em 20s...")
                        time.sleep(20)
                        continue
                else:
                    # Sistema conectado, monitorar normalmente
                    pass
                
                # Aguardar antes da próxima verificação
                time.sleep(10)
                
            except Exception as e:
                self.log_error(f"❌ Erro no loop de monitoramento: {e}")
                time.sleep(30)  # Aguarda mais tempo em caso de erro
        
        self.log_info("⏹️ Loop de monitoramento finalizado")

    def check_log_queue(self):
        """Verifica a fila de logs e atualiza a interface"""
        try:
            while True:
                level, message = self.log_queue.get_nowait()
                self.add_log_to_display(level, message)
        except queue.Empty:
            pass
        
        # Reagendar verificação
        self.root.after(100, self.check_log_queue)

    def add_log_to_display(self, level, message):
        """Adiciona uma mensagem de log à exibição"""
        timestamp = time.strftime("%H:%M:%S")
        
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, formatted_message)
        
        # Manter apenas as últimas 1000 linhas
        lines = self.log_text.get('1.0', tk.END).split('\n')
        if len(lines) > 1000:
            self.log_text.delete('1.0', f'{len(lines)-1000}.0')
        
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)

    def clear_logs(self):
        """Limpa a área de logs"""
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state='disabled')

    def log_info(self, message):
        """Log de informação"""
        self.logger.info(message)
        self.log_queue.put(('INFO', message))

    def log_warning(self, message):
        """Log de aviso"""
        self.logger.warning(message)
        self.log_queue.put(('WARNING', message))

    def log_error(self, message):
        """Log de erro"""
        self.logger.error(message)
        self.log_queue.put(('ERROR', message))

    def on_closing(self):
        """Chamado quando a janela é fechada"""
        if self.is_running:
            if messagebox.askokcancel("Fechar", "O sistema está em execução. Deseja realmente sair?"):
                self.stop_system()
                time.sleep(1)  # Aguarda thread terminar
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    """Função principal"""
    # Verificar se está sendo executado como script principal
    if __name__ != "__main__":
        return
    
    try:
        root = tk.Tk()
        RagnarokReconnectGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Erro fatal na GUI: {e}")
        messagebox.showerror("Erro Fatal", f"Erro ao inicializar a interface:\n{e}")

if __name__ == "__main__":
    main() 