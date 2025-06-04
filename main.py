import pyautogui
import time
import keyboard 
import os       

from funcoes import (
    verificar_desconexao,
    iniciar_processo_login_completo,
    clicar_para_focar_jogo, 
    log_error,
    log_info,
    log_aviso
)

# === INICIALIZAÇÃO DO INTERCEPTION ===
# Necessário para que os cliques do PIN funcionem corretamente
try:
    import interception
    log_info("Inicializando Interception para automação precisa...")
    interception.auto_capture_devices(keyboard=True, mouse=True)
    log_info("Interception inicializado com sucesso! Cliques serão mais precisos.")
except ImportError:
    log_aviso("Interception não disponível. Usando PyAutoGUI como fallback.")
    log_aviso("NOTA: Os cliques podem ser menos precisos sem o Interception.")
except Exception as e:
    log_error(f"Erro ao inicializar Interception: {e}")
    log_aviso("Continuando com PyAutoGUI como fallback.")

IMAGE_DISCONNECT = 'desconectado.png'
IMAGE_CONFIRM = 'confirmar.png'     
IMAGE_SENHA = 'senha.png'         
IMAGE_NAME = 'jogar.png'           
IMAGE_RAGNAROK_FOCUS = 'ragnarok.png' 
IMAGE_JOGAR = 'jogar.png'
IMAGE_PIN_FOLDER = '' 

GAME_WINDOW_TITLE = 'Ragnarok'

SENHA_DO_USUARIO = "5555"  
PIN_DO_USUARIO = "1234"     

# --- Configurações Gerais ---
CONFIANCA_IMAGEM_GERAL = 0.8 # Confiança padrão para a maioria das buscas de imagem
CONFIANCA_IMAGEM_FOCO = 0.8  # Confiança específica para a imagem de foco (ragnarok.png)
CONFIANCA_DESCONEXAO = 0.9 # Confiança mais alta para detectar a tela de desconexão
MONITOR_INTERVAL_SECONDS = 10 # Intervalo entre verificações quando o jogo está conectado
RETRY_DELAY_LOGIN_FAIL = 20 # Tempo de espera antes de tentar um novo ciclo de login após uma falha completa

# --- Variável Global e Função para Atalho de Teclado (Interrupção/Reset Manual) ---
_return_to_main_loop_flag = False

def set_return_flag_callback():
    """Callback para o atalho de teclado. Sinaliza para reiniciar o loop principal."""
    global _return_to_main_loop_flag
    _return_to_main_loop_flag = True
    # Usar print diretamente aqui pois as funções de log são de funcoes.py
    print(f"\n[{time.strftime('%H:%M:%S')}] [ATALHO] Ctrl+N detectado. Reiniciando loop principal na próxima iteração.")

# Registrar o atalho de teclado
try:
    keyboard.add_hotkey('ctrl+n', set_return_flag_callback)
    print(f"[{time.strftime('%H:%M:%S')}] [INFO] Atalho 'Ctrl+N' registrado para reiniciar o loop de monitoramento.")
except Exception as e_hotkey:
    print(f"[{time.strftime('%H:%M:%S')}] [ERRO] Não foi possível registrar o atalho 'Ctrl+N': {e_hotkey}. "
          "O programa continuará sem o atalho. Verifique as permissões se necessário.")

# --- Função Principal de Monitoramento ---
def monitorar_bot():
    """Função principal que monitora o estado do jogo e orquestra o processo de login."""
    print("="*60)
    print(f"[{time.strftime('%H:%M:%S')}] [INFO] Iniciando monitoramento principal do bot...")
    print(f"[{time.strftime('%H:%M:%S')}] [INFO] Pressione Ctrl+N para forçar o reinício do ciclo de verificação.")
    print(f"[{time.strftime('%H:%M:%S')}] [INFO] Pressione Ctrl+C no terminal para encerrar o bot.")
    print("="*60)

    while True:
        try:
            global _return_to_main_loop_flag
            if _return_to_main_loop_flag:
                _return_to_main_loop_flag = False # Reseta a flag
                print(f"[{time.strftime('%H:%M:%S')}] [INFO] Reiniciando ciclo principal devido ao atalho Ctrl+N.")
                time.sleep(1) # Pequena pausa
                continue # Volta ao início do while True

            # PASSO 1: Verificar se está desconectado
            # A função verificar_desconexao é simples e não tenta focar a janela
            if verificar_desconexao(image_path=IMAGE_DISCONNECT, confidence=CONFIANCA_DESCONEXAO):
                print(f"[{time.strftime('%H:%M:%S')}] [STATUS] Tela de desconexão ('{IMAGE_DISCONNECT}') detectada.")
                
                # PASSO 1.1: Tentar focar no jogo clicando em 'ragnarok.png' UMA VEZ após detectar desconexão.
                # Isso prepara o jogo para o processo de login.
                print(f"[{time.strftime('%H:%M:%S')}] [INFO] Tentando focar/ativar o jogo clicando em '{IMAGE_RAGNAROK_FOCUS}'...")
                if not clicar_para_focar_jogo(imagem_alvo_foco=IMAGE_RAGNAROK_FOCUS, 
                                            confianca_imagem=CONFIANCA_IMAGEM_FOCO):
                    # Usar a função log_error importada de funcoes.py
                    log_error(f"Falha crítica ao tentar focar no jogo com '{IMAGE_RAGNAROK_FOCUS}' após desconexão. "
                              f"Verifique se a imagem está visível. Aguardando {RETRY_DELAY_LOGIN_FAIL}s antes de tentar novamente o ciclo.")
                    time.sleep(RETRY_DELAY_LOGIN_FAIL)
                    continue # Tenta o ciclo de verificação de desconexão novamente

                print(f"[{time.strftime('%H:%M:%S')}] [INFO] Foco no jogo realizado (ou tentativa). Iniciando processo de login completo...")
                
                # PASSO 2: Se desconectado e o foco inicial foi tentado, iniciar o processo de login completo.
                login_sucesso = iniciar_processo_login_completo(
                    senha=SENHA_DO_USUARIO, 
                    pin=PIN_DO_USUARIO, 
                    pasta_imagens_pin=IMAGE_PIN_FOLDER,
                    image_confirm=IMAGE_CONFIRM, 
                    image_senha_screen=IMAGE_SENHA,
                    image_name=IMAGE_NAME,
                    image_ragnarok_focus=IMAGE_RAGNAROK_FOCUS, # Passa para uso interno no login (ex: antes de 'jogar.png')
                    image_jogar=IMAGE_JOGAR,
                    confianca_geral=CONFIANCA_IMAGEM_GERAL,
                    confianca_foco=CONFIANCA_IMAGEM_FOCO
                )

                if login_sucesso:
                    print(f"[{time.strftime('%H:%M:%S')}] [STATUS] Login completo bem-sucedido. Retornando ao monitoramento de desconexão.")
                    time.sleep(MONITOR_INTERVAL_SECONDS)
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] [ERRO] Processo de login completo falhou. "
                          f"Aguardando {RETRY_DELAY_LOGIN_FAIL}s antes de tentar novamente o ciclo.")
                    time.sleep(RETRY_DELAY_LOGIN_FAIL)
                continue # Volta ao início do while True para reavaliar o estado

            else:
                # Se não estiver desconectado, apenas aguarda e monitora.
                print(f"[{time.strftime('%H:%M:%S')}] [STATUS] Jogo aparentemente conectado. Monitorando desconexão a cada {MONITOR_INTERVAL_SECONDS}s.")
                time.sleep(MONITOR_INTERVAL_SECONDS) 
                continue 

        except pyautogui.FailSafeException:
            print(f"\n[{time.strftime('%H:%M:%S')}] [EMERGÊNCIA] Fail-safe do PyAutoGUI ativado (mouse no canto superior esquerdo). Encerrando o bot.")
            break 
        except KeyboardInterrupt:
            print(f"\n[{time.strftime('%H:%M:%S')}] [INFO] Monitoramento interrompido pelo usuário (Ctrl+C). Encerrando o bot.")
            break 
        except Exception as e_main_loop:
            print(f"[{time.strftime('%H:%M:%S')}] [ERRO FATAL] Erro inesperado no loop principal de monitoramento: {type(e_main_loop).__name__} - {e_main_loop}")
            print(f"[{time.strftime('%H:%M:%S')}] [INFO] Stack trace do erro:", exc_info=True) # Adiciona stack trace para depuração
            print(f"[{time.strftime('%H:%M:%S')}] [INFO] Aguardando 30 segundos antes de tentar reiniciar o ciclo...")
            time.sleep(30) # Uma pausa mais longa para erros inesperados graves
            continue 
        finally:
            # Esta seção finally não é estritamente necessária aqui dentro do loop,
            # mas o unhook do teclado é bom ao final do programa.
            pass

    # Código a ser executado quando o loop principal é quebrado (ex: Ctrl+C, FailSafe)
    print(f"[{time.strftime('%H:%M:%S')}] [INFO] Loop de monitoramento principal finalizado.")
    try:
        keyboard.unhook_all() # Remove todos os atalhos registrados
        print(f"[{time.strftime('%H:%M:%S')}] [INFO] Atalhos de teclado desregistrados.")
    except Exception as e_unhook_final:
        print(f"[{time.strftime('%H:%M:%S')}] [AVISO] Erro ao tentar desregistrar atalhos na finalização: {e_unhook_final}")

# --- Bloco de Execução Principal ---
if __name__ == "__main__":
    print(f"[{time.strftime('%H:%M:%S')}] [INFO] Iniciando script...")

    # Validações iniciais críticas
    if SENHA_DO_USUARIO == "Sua Senha" or not SENHA_DO_USUARIO:
        print(f"[{time.strftime('%H:%M:%S')}] [ERRO FATAL] SENHA_DO_USUARIO não foi configurada. Edite o script e defina sua senha.")
        exit()
    if PIN_DO_USUARIO == "Seu Pin" or not (PIN_DO_USUARIO.isdigit() and len(PIN_DO_USUARIO) == 4) :
        print(f"[{time.strftime('%H:%M:%S')}] [ERRO FATAL] PIN_DO_USUARIO ('{PIN_DO_USUARIO}') é inválido ou não configurado. "
              "Deve ser uma string de 4 dígitos numéricos.")
        exit()

    # Verificar se as imagens principais existem (opcional, mas bom para debug inicial)
    imagens_criticas = {
        "Desconexão": IMAGE_DISCONNECT,
        "Foco Principal": IMAGE_RAGNAROK_FOCUS,
        "Confirmar": IMAGE_CONFIRM,
        "Tela Senha": IMAGE_SENHA,
        "Botão Jogar": IMAGE_JOGAR,
        "Nome Personagem": IMAGE_NAME
    }
    print(f"[{time.strftime('%H:%M:%S')}] [INFO] Verificando existência das imagens críticas...")
    todas_imagens_ok = True
    for nome_amigavel, caminho_imagem in imagens_criticas.items():
        if not os.path.exists(caminho_imagem):
            print(f"[{time.strftime('%H:%M:%S')}] [ERRO FATAL] Imagem crítica '{nome_amigavel}' ('{caminho_imagem}') não encontrada na pasta do script.")
            todas_imagens_ok = False
    if not todas_imagens_ok:
        print(f"[{time.strftime('%H:%M:%S')}] [ERRO FATAL] Uma ou mais imagens críticas não foram encontradas. O bot não pode iniciar.")
        exit()
    print(f"[{time.strftime('%H:%M:%S')}] [INFO] Todas as imagens críticas verificadas com sucesso.")
    
    print(f"[{time.strftime('%H:%M:%S')}] [INFO] Senha configurada (comprimento: {len(SENHA_DO_USUARIO)}).")
    print(f"[{time.strftime('%H:%M:%S')}] [INFO] PIN configurado (comprimento: {len(PIN_DO_USUARIO)}).")

    # Inicia o monitoramento principal do bot
    monitorar_bot()
    
    print(f"[{time.strftime('%H:%M:%S')}] [INFO] Script finalizado.")