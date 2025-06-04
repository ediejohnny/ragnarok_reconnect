import os
import time
import pyautogui
import logging
import psutil
import cv2
import numpy as np

# Configura o logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Exibe logs no console
        # Opcional: logging.FileHandler('digitar_pin.log')  # Salva logs em um arquivo
    ]
)

# Sistema de logs global - pode ser redirecionado pela GUI
_gui_logger = None

def set_gui_logger(logger):
    """Permite que a GUI configure o logger global para funcoes.py"""
    global _gui_logger
    _gui_logger = logger

def log_info(message):
    """Log de informação - compatível com GUI e console"""
    if _gui_logger:
        _gui_logger.info(message)
    else:
        print(f"[funcoes.py INFO] {message}")

def log_error(message):
    """Log de erro - compatível com GUI e console"""
    if _gui_logger:
        _gui_logger.error(message)
    else:
        print(f"[funcoes.py ERRO] {message}")

def log_status(message):
    """Log de status - compatível com GUI e console"""
    if _gui_logger:
        _gui_logger.info(f"[STATUS] {message}")
    else:
        print(f"[funcoes.py STATUS] {message}")

def log_aviso(message):
    """Log de aviso - compatível com GUI e console"""
    if _gui_logger:
        _gui_logger.warning(message)
    else:
        print(f"[funcoes.py AVISO] {message}")

try:
    from interception import press as press_interception, click as click_interception
    def press(key):
        press_interception(key)
    def click(x, y, button):
        click_interception(x, y, button)
    log_info("Módulo 'interception' importado com sucesso e funções 'press' e 'click' configuradas para usá-lo.")
except ImportError as e:
    log_error(f"Não foi possível importar de 'interception': {e}")
    log_aviso("Funções de 'interception' serão substituídas por 'pyautogui' para compatibilidade.")
    def press(key):
        pyautogui.press(key)
        log_info(f"[FALLBACK] Usando pyautogui.press('{key}').")
    def click(x, y, button): # Esta é a função pyautogui.click
        pyautogui.click(x=x, y=y, button=button)
        log_info(f"[FALLBACK] Usando pyautogui.click({x}, {y}, button='{button}').")

# --- NOVA FUNÇÃO PARA FOCAR NO JOGO COM DETECÇÃO DE MOVIMENTO DO MOUSE ---
def clicar_para_focar_jogo(imagem_alvo_foco, confianca_imagem=0.8, max_tentativas_foco=5, delay_mouse_movido=3):
    """
    Procura a imagem_alvo_foco (ex: 'ragnarok.png') e clica nela com interception.
    Se o mouse for movido durante a tentativa, espera e tenta novamente.
    Retorna True se o clique foi bem-sucedido, False caso contrário.
    """
    log_info(f"Iniciando 'clicar_para_focar_jogo' em '{imagem_alvo_foco}'.")
    tentativas_foco = 0
    while tentativas_foco < max_tentativas_foco:
        tentativas_foco += 1
        log_info(f"Tentativa {tentativas_foco}/{max_tentativas_foco} para focar em '{imagem_alvo_foco}'.")
        pos_mouse_antes = pyautogui.position()
        coords_alvo = None
        try:
            coords_alvo = pyautogui.locateCenterOnScreen(imagem_alvo_foco, confidence=confianca_imagem)
            if coords_alvo:
                log_info(f"Imagem '{imagem_alvo_foco}' encontrada em {coords_alvo}.")
                # Uma pequena pausa para o usuário ter chance de mover o mouse se estiver usando
                time.sleep(0.2)
                pos_mouse_depois_busca = pyautogui.position()

                if pos_mouse_antes != pos_mouse_depois_busca:
                    log_aviso(f"Movimento do mouse detectado (Antes: {pos_mouse_antes}, Depois: {pos_mouse_depois_busca}). "
                              f"Aguardando {delay_mouse_movido}s antes de tentar novamente.")
                    time.sleep(delay_mouse_movido)
                    continue # Próxima iteração do while para tentar novamente

                # Se não houve movimento, prossegue com o clique
                click(x=coords_alvo.x, y=coords_alvo.y, button='left') # Usa o click do interception
                log_info(f"Clique (interception) realizado em '{imagem_alvo_foco}' em {coords_alvo} para focar.")
                time.sleep(1.0) # Pequena pausa após o clique
                return True
            else:
                log_aviso(f"Imagem '{imagem_alvo_foco}' não encontrada na tentativa {tentativas_foco}.")
                if tentativas_foco < max_tentativas_foco:
                    time.sleep(1) # Espera antes da próxima tentativa de localizar
        except pyautogui.ImageNotFoundException:
            log_aviso(f"Imagem '{imagem_alvo_foco}' não encontrada (exceção) na tentativa {tentativas_foco}.")
            if tentativas_foco < max_tentativas_foco:
                time.sleep(1)
        except NameError: # Especificamente para o caso de 'click' do interception não estar definido
            log_error("A função 'click' do 'interception' não está disponível. Não é possível focar no jogo.")
            return False # Falha crítica
        except Exception as e:
            log_error(f"Erro ao tentar focar em '{imagem_alvo_foco}': {type(e).__name__} - {e}")
            if tentativas_foco < max_tentativas_foco:
                time.sleep(1)

    log_error(f"Não foi possível focar no jogo clicando em '{imagem_alvo_foco}' após {max_tentativas_foco} tentativas.")
    return False

# --- Funções Auxiliares Existentes (com melhorias e uso do logger) ---

def enviar_enter(): # Mantida conforme a sugestão anterior
    log_info("Iniciando 'enviar_enter'...")
    try:
        press('enter')
        backend_module = getattr(press, '__module__', 'desconhecido')
        if 'interception' in backend_module:
             log_info("Enter enviado via 'press(\\'enter\\')' (usando interception).")
        elif hasattr(pyautogui, 'press') and press.__code__ == pyautogui.press.__code__ :
            log_info("Enter enviado via 'press(\\'enter\\')' (usando pyautogui).")
        else:
            log_info(f"Enter enviado via 'press(\\'enter\\')' (usando backend: {backend_module}).")
    except Exception as e:
        log_error(f"Falha ao enviar Enter usando a função 'press' configurada: {e}")
    time.sleep(0.5)

def preencher_e_logar(senha_digitada):
    # Esta função não precisa mais se preocupar em ativar a janela
    log_info("Iniciando 'preencher_e_logar' para a senha...")
    try:
        press('tab')
        log_info("Tab enviado para focar no campo de senha.")
        time.sleep(0.3)
        log_info(f"Tentando digitar senha: {'*' * len(senha_digitada)}")
        log_info("Digitando senha caracter por caracter para maior compatibilidade...")
        for char_senha in senha_digitada:
            try:
                press(char_senha)
                time.sleep(0.1)
            except Exception as e_char:
                log_error(f"Falha ao digitar o caracter '{char_senha}': {e_char}")
        log_info("Senha enviada caracter por caracter.")
        time.sleep(0.3)
        press('enter')
        log_info("Enter enviado para submeter a senha.")
        return True
    except Exception as e:
        log_error(f"Falha em 'preencher_e_logar': {e}")
        return False

def digitar_pin_numerico(pin_str, pasta_imagens_pin="", confianca_imagem=0.75):
    log_info(f"Iniciando digitação do PIN com template matching (dígitos: {'*' * len(pin_str)}).")
    
    if not pin_str.isdigit() or len(pin_str) < 4:
        log_error(f"PIN inválido: '{pin_str}'. Deve ter 4 dígitos numéricos.")
        return False

    def capture_screen():
        """Captura a tela inteira"""
        screenshot = pyautogui.screenshot()
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def save_screenshot_with_analysis(image, filename, positions=None):
        """Salva o screenshot com marcações das posições detectadas"""
        annotated = image.copy()
        
        if positions:
            for key, (x, y) in positions.items():
                # Desenha um círculo na posição detectada
                cv2.circle(annotated, (int(x), int(y)), 15, (0, 255, 0), 3)
                # Desenha cruz para precisão
                cv2.line(annotated, (int(x)-20, int(y)), (int(x)+20, int(y)), (0, 255, 0), 2)
                cv2.line(annotated, (int(x), int(y)-20), (int(x), int(y)+20), (0, 255, 0), 2)
                # Adiciona texto identificando o botão
                cv2.putText(annotated, str(key), (int(x)-15, int(y)-30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        cv2.imwrite(filename, annotated)
        log_info(f"Screenshot com análise salvo: {filename}")

    def load_template_images(pasta_imagens_pin):
        """Carrega as imagens template dos números e botão confirmar"""
        templates = {}
        
        # Carrega imagens dos números 0-9
        for i in range(10):
            template_path = os.path.join(pasta_imagens_pin, f"{i}.png")
            if os.path.exists(template_path):
                template = cv2.imread(template_path, cv2.IMREAD_COLOR)
                if template is not None:
                    templates[str(i)] = template
                    log_info(f"Template {i}.png carregado: {template.shape}")
                else:
                    log_error(f"Erro ao carregar {template_path}")
            else:
                log_error(f"Arquivo {template_path} não encontrado")
        
        # Carrega imagem do botão Confirmar
        confirmar_path = os.path.join(pasta_imagens_pin, "confirmar.png")
        if os.path.exists(confirmar_path):
            template = cv2.imread(confirmar_path, cv2.IMREAD_COLOR)
            if template is not None:
                templates['confirmar'] = template
                log_info(f"Template confirmar.png carregado: {template.shape}")
            else:
                log_error(f"Erro ao carregar {confirmar_path}")
        else:
            log_error(f"Arquivo {confirmar_path} não encontrado")
        
        log_info(f"Total de templates carregados: {len(templates)}")
        return templates

    def wait_for_pin_interface(templates, max_wait_time=30, check_interval=2):
        """Espera a interface do PIN aparecer antes de começar"""
        log_info(f"Aguardando interface do PIN aparecer (máximo {max_wait_time}s)...")
        
        start_time = time.time()
        attempt = 1
        
        while time.time() - start_time < max_wait_time:
            log_info(f"Tentativa {attempt}: Verificando se interface do PIN está visível...")
            
            # Captura tela atual
            image = capture_screen()
            
            # Verifica se pelo menos alguns números estão visíveis
            found_numbers = []
            for digit in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                if digit in templates:
                    result = cv2.matchTemplate(image, templates[digit], cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, _ = cv2.minMaxLoc(result)
                    if max_val >= 0.7:  # Threshold mais baixo para detecção
                        found_numbers.append(digit)
            
            log_info(f"Números visíveis: {found_numbers} ({len(found_numbers)} de 10)")
            
            # Se encontrou pelo menos 5 números diferentes, a interface provavelmente está visível
            if len(found_numbers) >= 5:
                log_info(f"Interface do PIN detectada! Encontrados {len(found_numbers)} números visíveis")
                # Salva screenshot da interface detectada
                save_screenshot_with_analysis(image, "pin_interface_detected.png")
                return True
            
            log_info(f"Interface ainda não visível. Aguardando {check_interval}s...")
            time.sleep(check_interval)
            attempt += 1
        
        log_error(f"Timeout: Interface do PIN não apareceu em {max_wait_time}s")
        return False

    def find_all_template_matches(screen_image, templates, threshold=0.7):
        """Encontra todas as correspondências de templates na tela"""
        all_positions = {}
        
        for key, template in templates.items():
            log_info(f"Procurando todas as instâncias de: {key}")
            
            # Template matching
            result = cv2.matchTemplate(screen_image, template, cv2.TM_CCOEFF_NORMED)
            
            # Encontra todas as correspondências acima do threshold
            locations = np.where(result >= threshold)
            
            matches = []
            template_h, template_w = template.shape[:2]
            
            for pt in zip(*locations[::-1]):  # Switch columns and rows
                center_x = pt[0] + template_w // 2
                center_y = pt[1] + template_h // 2
                confidence = result[pt[1], pt[0]]
                matches.append((center_x, center_y, confidence))
            
            if matches:
                # Ordena por confiança (maior primeiro)
                matches.sort(key=lambda x: x[2], reverse=True)
                all_positions[key] = matches
                log_info(f"{key}: {len(matches)} correspondências encontradas")
                for i, (x, y, conf) in enumerate(matches[:3]):  # Mostra apenas as 3 melhores
                    log_info(f"  {i+1}º: ({x}, {y}) confiança {conf:.3f}")
            else:
                log_info(f"{key}: nenhuma correspondência encontrada")
        
        return all_positions

    def click_number_with_template_matching(number, step, templates, max_retries=3):
        """Clica em um número usando template matching com retry"""
        log_info(f"PASSO {step}: CLICANDO NO NÚMERO {number} (TEMPLATE MATCHING)")
        
        for retry in range(max_retries):
            if retry > 0:
                log_info(f"Tentativa {retry + 1}/{max_retries}")
                time.sleep(1)  # Aguarda antes de tentar novamente
            
            # Captura a tela antes do clique
            log_info("Capturando tela...")
            image = capture_screen()
            filename = f"template_step_{step}_attempt_{retry + 1}_before.png"
            
            # Encontra todas as posições dos templates
            log_info("Analisando templates na imagem...")
            all_positions = find_all_template_matches(image, templates, threshold=0.7)
            
            # Seleciona a melhor posição para este número
            if str(number) in all_positions and all_positions[str(number)]:
                best_match = all_positions[str(number)][0]
                x, y = best_match[0], best_match[1]
                confidence = best_match[2]
                
                log_info(f"Posição encontrada para {number}: ({x}, {y}) com confiança {confidence:.3f}")
                
                # Cria um dicionário com apenas esta posição para o screenshot
                single_position = {str(number): (x, y)}
                save_screenshot_with_analysis(image, filename, single_position)
                
                # Move o mouse e clica usando a função click configurada
                log_info(f"Movendo mouse para ({x}, {y})")
                try:
                    click(x, y, 'left')  # Usa a função click configurada (interception ou pyautogui)
                    log_info(f"Clique no número {number} realizado com sucesso")
                    
                    # === MOVIMENTO DO MOUSE APÓS CLIQUE ===
                    # Move o mouse 300 pixels para a direita após clicar no número
                    nova_posicao_x = x + 300
                    log_info(f"Movendo mouse 300 pixels para a direita: ({x}, {y}) -> ({nova_posicao_x}, {y})")
                    try:
                        # Usa pyautogui para mover o mouse (mais confiável para movimento)
                        pyautogui.moveTo(nova_posicao_x, y)
                        log_info(f"Mouse movido para ({nova_posicao_x}, {y})")
                    except Exception as e_move:
                        log_aviso(f"Erro ao mover mouse para a direita: {e_move}")
                    
                    # Aguarda 1 segundo antes de prosseguir
                    log_info("Aguardando 1 segundo após movimento do mouse...")
                    time.sleep(1)
                    
                    # Aguarda um pouco para a interface atualizar
                    time.sleep(0.5)
                    
                    # Captura a tela após o clique
                    log_info("Capturando tela após o clique...")
                    image_after = capture_screen()
                    filename_after = f"template_step_{step}_attempt_{retry + 1}_after.png"
                    save_screenshot_with_analysis(image_after, filename_after)
                    
                    log_info(f"Número {number} clicado com sucesso usando template matching!")
                    return True
                except Exception as e_click:
                    log_error(f"Erro ao clicar no número {number}: {e_click}")
                    continue
            else:
                log_error(f"Número {number} não encontrado na tentativa {retry + 1}")
                save_screenshot_with_analysis(image, filename)
        
        log_error(f"Falha ao clicar no número {number} após {max_retries} tentativas")
        return False

    def click_confirmar_with_template_matching(templates, max_retries=3):
        """Clica no botão Confirmar usando template matching com retry"""
        log_info("CLICANDO NO BOTÃO CONFIRMAR (TEMPLATE MATCHING)")
        
        for retry in range(max_retries):
            if retry > 0:
                log_info(f"Tentativa {retry + 1}/{max_retries}")
                time.sleep(1)
            
            # Captura a tela
            log_info("Capturando tela...")
            image = capture_screen()
            
            # Encontra o botão Confirmar
            log_info("Procurando botão Confirmar...")
            all_positions = find_all_template_matches(image, {'confirmar': templates['confirmar']}, threshold=0.7)
            
            if 'confirmar' in all_positions and all_positions['confirmar']:
                best_match = all_positions['confirmar'][0]
                x, y = best_match[0], best_match[1]
                confidence = best_match[2]
                
                log_info(f"Botão Confirmar encontrado em: ({x}, {y}) com confiança {confidence:.3f}")
                
                # Salva screenshot
                single_position = {'confirmar': (x, y)}
                save_screenshot_with_analysis(image, f"template_confirmar_attempt_{retry + 1}.png", single_position)
                
                # Clica no botão
                log_info("Clicando em Confirmar")
                try:
                    click(x, y, 'left')  # Usa a função click configurada
                    log_info("Botão Confirmar clicado com sucesso!")
                    return True
                except Exception as e_click:
                    log_error(f"Erro ao clicar no botão Confirmar: {e_click}")
                    continue
            else:
                log_error(f"Botão Confirmar não encontrado na tentativa {retry + 1}")
                save_screenshot_with_analysis(image, f"template_confirmar_not_found_attempt_{retry + 1}.png")
        
        log_error(f"Falha ao clicar no botão Confirmar após {max_retries} tentativas")
        return False

    # === FUNÇÃO PRINCIPAL ===
    try:
        # Carrega as imagens template
        log_info("Carregando templates...")
        templates = load_template_images(pasta_imagens_pin)
        
        if not templates:
            log_error("Nenhum template foi carregado! Verifique se as imagens estão no diretório.")
            return False
        
        # Aguarda a interface do PIN aparecer
        if not wait_for_pin_interface(templates):
            log_error("Interface do PIN não apareceu. Abortando...")
            return False
        
        log_info(f"Iniciando sequência do código: {pin_str}")
        
        # Clica em cada número usando template matching
        success_count = 0
        for i, digit in enumerate(pin_str):
            if click_number_with_template_matching(digit, i + 1, templates):
                success_count += 1
                log_info(f"Progresso: {success_count}/{len(pin_str)} números inseridos")
            else:
                log_error(f"Falha no dígito {digit} (posição {i + 1})")
            
            if i < len(pin_str) - 1:  # Aguarda entre cliques (exceto no último)
                log_info("Aguardando 2 segundos antes do próximo número...")
                time.sleep(2)
        
        log_info(f"Resultado final: {success_count}/{len(pin_str)} números clicados com sucesso")
        
        if success_count == len(pin_str):
            log_info("Todos os números foram inseridos! Procedendo para confirmação...")
            
            # Aguarda antes de confirmar
            log_info("Aguardando 2 segundos antes de confirmar...")
            time.sleep(2)
            
            # Clica em Confirmar
            if 'confirmar' in templates and click_confirmar_with_template_matching(templates):
                log_info("OPERAÇÃO CONCLUÍDA COM SUCESSO TOTAL!")
                log_info(f"PIN {pin_str} inserido e confirmado!")
                
                # === NOVO: CLICAR NO BOTÃO "JOGAR" ===
                log_info("Passo adicional: Procurando botão 'Jogar'...")
                
                # Aguarda um pouco para a tela carregar
                time.sleep(3)
                
                # Procura e clica no botão Jogar
                jogar_encontrado = False
                max_tentativas_jogar = 10
                
                for tentativa_jogar in range(1, max_tentativas_jogar + 1):
                    log_info(f"Tentativa {tentativa_jogar}/{max_tentativas_jogar}: Procurando jogar.png...")
                    
                    try:
                        coords_jogar = pyautogui.locateCenterOnScreen('jogar.png', confidence=0.8)
                        if coords_jogar:
                            log_info(f"Botão 'Jogar' encontrado em {coords_jogar}")
                            
                            # Clica no botão Jogar
                            click(coords_jogar.x, coords_jogar.y, 'left')
                            log_info("Clique no botão 'Jogar' realizado com sucesso!")
                            
                            # Move o mouse para a direita após clicar
                            nova_posicao_x = coords_jogar.x + 300
                            log_info(f"Movendo mouse 300 pixels para a direita após 'Jogar': ({coords_jogar.x}, {coords_jogar.y}) -> ({nova_posicao_x}, {coords_jogar.y})")
                            try:
                                pyautogui.moveTo(nova_posicao_x, coords_jogar.y)
                                log_info(f"Mouse movido para ({nova_posicao_x}, {coords_jogar.y})")
                            except Exception as e_move_jogar:
                                log_aviso(f"Erro ao mover mouse após 'Jogar': {e_move_jogar}")
                            
                            time.sleep(1)  # Aguarda após movimento
                            jogar_encontrado = True
                            break
                        else:
                            log_info(f"Botão 'Jogar' não encontrado na tentativa {tentativa_jogar}")
                            if tentativa_jogar < max_tentativas_jogar:
                                time.sleep(2)  # Aguarda antes da próxima tentativa
                    
                    except pyautogui.ImageNotFoundException:
                        log_info(f"jogar.png não encontrado (exceção) na tentativa {tentativa_jogar}")
                        if tentativa_jogar < max_tentativas_jogar:
                            time.sleep(2)
                    except Exception as e_jogar:
                        log_error(f"Erro ao procurar jogar.png na tentativa {tentativa_jogar}: {e_jogar}")
                        if tentativa_jogar < max_tentativas_jogar:
                            time.sleep(2)
                
                if jogar_encontrado:
                    log_info("✅ SEQUÊNCIA COMPLETA: PIN + Confirmar + Jogar realizada com sucesso!")
                    log_info("📋 RETORNANDO: O sistema pode agora retornar ao monitoramento de desconexão")
                    
                    # Aguarda um pouco para o jogo carregar
                    time.sleep(5)
                    return True
                else:
                    log_aviso(f"⚠️ Botão 'Jogar' não foi encontrado após {max_tentativas_jogar} tentativas")
                    log_aviso("PIN foi inserido e confirmado, mas não foi possível clicar em 'Jogar'")
                    return True  # Considera sucesso parcial
                
            else:
                log_aviso(f"PIN {pin_str} inserido, mas falha ao clicar em Confirmar")
                return True  # Considera sucesso parcial
        else:
            log_error(f"Operação FALHOU. Apenas {success_count} de {len(pin_str)} números foram clicados.")
            return False
            
    except Exception as e:
        log_error(f"Erro inesperado na digitação do PIN: {e}")
        return False

def encerrar_aplicativo_jogo(game_window_title):
    # Esta função pode permanecer como está, pois lida com o fechamento geral do app
    log_info(f"Tentando encerrar o aplicativo com o título '{game_window_title}'...")
    # ... (restante da função mantida como no seu original)
    try:
        game_windows = pyautogui.getWindowsWithTitle(game_window_title)
        if game_windows:
            for window in game_windows:
                try: # Adicionado try-except para falhas individuais ao fechar
                    window.close()
                    log_info(f"Janela '{game_window_title}' (PID {window._hWnd}) fechada via pyautogui.close().") # Usar _hWnd se disponível para ID único
                    time.sleep(0.5)
                except Exception as e_close:
                    log_aviso(f"Falha ao tentar fechar uma janela '{game_window_title}': {e_close}")
        else:
            log_aviso(f"Nenhuma janela com o título '{game_window_title}' encontrada para fechar via pyautogui.")

        process_names_to_check = ['Ragnarok.exe', 'Ragexe.exe', 'client.exe'] # Mantido
        
        found_and_terminated = False
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.name() is None:
                    continue
                for name in process_names_to_check:
                    if name.lower() in proc.name().lower():
                        log_info(f"Processo do jogo encontrado: PID={proc.pid}, Nome='{proc.name()}'")
                        proc.terminate()

                        log_info(f"Processo do jogo (PID {proc.pid}) encerrado via psutil.")
                        time.sleep(1)
                        found_and_terminated = True
                        break
                if found_and_terminated:
                    break 
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e_proc:
                log_aviso(f"Erro ao acessar/terminar processo {proc.pid if proc else 'desconhecido'}: {e_proc}")
                continue
            except Exception as e_proc_generic:
                log_error(f"Erro inesperado com processo {proc.pid if proc else 'desconhecido'} '{proc.name() if proc else ''}': {e_proc_generic}")
                continue

        if found_and_terminated:
            log_info("Aplicativo do jogo encerrado com sucesso.")
            return True
        else:
            log_aviso("Não foi possível encontrar ou encerrar o processo do jogo com os nomes verificados via psutil.")
            return False # Pode retornar False se apenas o fechamento da janela falhou mas o processo não foi encontrado
    except Exception as e:
        log_error(f"Erro ao tentar encerrar o aplicativo do jogo: {e}")
        return False


# --- FUNÇÕES CHAVE PARA O FLUXO ---

# A ANTIGA _ativar_janela_local FOI REMOVIDA E SUA LÓGICA SUBSTITUÍDA POR 'clicar_para_focar_jogo'
# que será chamada APENAS UMA VEZ no main.py após detectar 'desconectado.png'

def procurar_e_interagir_imagem(image_path, confidence, attempts=1, delay_between_attempts=1, action='click'): # Removido game_window_title
    """
    Procura por uma imagem na tela e realiza uma ação.
    NÃO tenta mais ativar a janela internamente. Assume que o jogo já está focado.
    """
    log_info(f"Procurando por '{image_path}' para '{action}' (confiança: {confidence}, tentativas: {attempts})...")
    coords = None
    for tentativa in range(attempts):
        # REMOVIDO: _ativar_janela_local(game_window_title)
        try:
            coords = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if coords:
                log_info(f"'{image_path}' encontrado em {coords} (tentativa {tentativa + 1}).")
                if action == 'click':
                    click(x=coords.x, y=coords.y, button='left') # Usa click do interception
                    log_info(f"Clique em '{image_path}' realizado.")
                elif action == 'press_enter':
                    enviar_enter()
                    log_info(f"Enter enviado após encontrar '{image_path}'.")
                elif action == 'none':
                    log_info(f"Ação 'none' para '{image_path}' realizada (apenas localização).")
                else:
                    log_error(f"Ação '{action}' desconhecida para '{image_path}'.")
                    return False
                time.sleep(1) # Ajustado para 1s após interação
                return True
            else: # (Lógica de imagem não encontrada mantida)
                log_aviso(f"'{image_path}' não encontrado na tentativa {tentativa + 1}. Nova tentativa em {delay_between_attempts}s...")
                time.sleep(delay_between_attempts)
        # (Restante dos excepts mantidos, especialmente NameError para 'click' ou 'press')
        except pyautogui.ImageNotFoundException:
            log_aviso(f"'{image_path}' não encontrado (exceção ImageNotFoundException) na tentativa {tentativa + 1}. Nova tentativa em {delay_between_attempts}s...")
            time.sleep(delay_between_attempts)
        except NameError:
            log_error(f"Função 'click' ou 'press' (interception) não importada. Não é possível interagir com '{image_path}'.")
            return False # Falha crítica
        except Exception as e:
            log_error(f"Erro ao buscar/interagir com '{image_path}': {type(e).__name__} - {e}. Nova tentativa em {delay_between_attempts}s...")
            time.sleep(delay_between_attempts)

    log_aviso(f"'{image_path}' NÃO foi encontrado após {attempts} tentativas ou a interação falhou.")
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    screenshot_filename = f"debug_image_not_found_{os.path.basename(image_path).replace('.png', '')}_{timestamp}.png"
    try:
        pyautogui.screenshot(screenshot_filename)
        log_info(f"Screenshot de depuração salvo como: {screenshot_filename}")
    except Exception as e_screenshot:
        log_error(f"Falha ao salvar screenshot de depuração: {e_screenshot}")
    return False

def verificar_desconexao(image_path='desconectado.png', confidence=0.9): # Removido game_window_title
    """
    Verifica se a tela de desconexão está visível.
    NÃO tenta mais ativar a janela internamente.
    """
    log_info(f"Verificando tela de desconexão ('{image_path}')...")
    # REMOVIDO: if not _ativar_janela_local(game_window_title): ...
    try:
        coords = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if coords:
            log_info(f"Tela de desconexão '{image_path}' DETECTADA.")
            return True
        else:
            log_info(f"Tela de desconexão '{image_path}' NÃO detectada.")
            return False
    except pyautogui.ImageNotFoundException:
        log_info(f"Tela de desconexão '{image_path}' NÃO detectada (exceção ImageNotFoundException).")
        return False
    except Exception as e:
        log_error(f"Erro inesperado ao verificar tela de desconexão: {type(e).__name__} - {e}")
        return False

def iniciar_processo_login_completo(senha, pin, pasta_imagens_pin,
                                   image_confirm='confirmar.png',
                                   image_senha_screen='senha.png',
                                   image_name='name.png',             # Imagem do ID do jogador/seleção de personagem
                                   image_ragnarok_focus='ragnarok.png', # Imagem para foco geral/reset UI
                                   image_jogar='jogar.png',            # Imagem do botão "Jogar" ou similar
                                   confianca_geral=0.8,
                                   confianca_foco=0.8):              # Confiança para a imagem de foco
    log_info(">>> Iniciando PROCESSO DE LOGIN COMPLETO <<<")

    # PASSO 1: Confirmar (inicial) - Geralmente após abrir o patcher/jogo.
    # A função procurar_e_interagir_imagem já não faz mais o refoco interno com ragnarok.png.
    # O refoco inicial é feito em main.py após a desconexão.
    log_info("Passo 1: Confirmar (após 60 segundos de espera)")
    time.sleep(10)
    if not procurar_e_interagir_imagem(image_path=image_confirm, 
                                     confidence=confianca_geral, 
                                     attempts=10, 
                                     action='press_enter'):
        log_error("Falha no Passo 1 (confirmar inicial). Login abortado.")
        return False
    time.sleep(2) # Pausa para a próxima tela carregar

    # PASSO 2: Tela de Senha e Preenchimento
    log_info("Passo 2: Tela de Senha e Preenchimento")
    if not procurar_e_interagir_imagem(image_path=image_senha_screen, 
                                     confidence=confianca_geral, 
                                     attempts=5, 
                                     action='none'): # Apenas localizar
        log_error(f"Tela de senha ('{image_senha_screen}') não encontrada. Login abortado.")
        return False
    
    if not preencher_e_logar(senha): # preencher_e_logar usa 'press' e 'enviar_enter'
        log_error("Falha ao preencher/submeter senha. Login abortado.")
        return False
    time.sleep(3) # Pausa para processar login/servidor

    # PASSO 2.5: Enter para confirmar o servidor (após digitar a senha)
    log_info("Passo 2.5: Enter para confirmar o servidor (após senha)")
    enviar_enter()
    time.sleep(3) # Pausa para carregar tela de PIN

    # PASSO 2.8: Aguardar avatar_pin.png aparecer antes de digitar o PIN
    log_info("Passo 2.8: Aguardando avatar_pin.png aparecer...")
    if not procurar_e_interagir_imagem(image_path='avatar_pin.png', 
                                     confidence=confianca_geral, 
                                     attempts=10, 
                                     delay_between_attempts=2,
                                     action='none'): # Apenas detectar, não clicar
        log_error("Avatar PIN não detectado. Prosseguindo com digitação do PIN mesmo assim...")
    else:
        log_info("Avatar PIN detectado! Aguardando 2 segundos antes de iniciar digitação...")
        time.sleep(2) # Aguarda 2 segundos após detectar avatar_pin.png

    # PASSO 3: Digitação do PIN
    log_info("Passo 3: Digitação do PIN")
    if not digitar_pin_numerico(pin, pasta_imagens_pin, confianca_imagem=confianca_geral):
        log_error("Falha ao digitar o PIN. Login abortado.")
        return False
    
    # A função digitar_pin_numerico agora faz TUDO:
    # - Digita o PIN
    # - Clica em Confirmar  
    # - Clica em Jogar
    # - Retorna para o main.py continuar o monitoramento
    
    log_info(">>> PROCESSO DE LOGIN COMPLETO CONCLUÍDO COM SUCESSO! <<<")
    log_info("A função digitar_pin_numerico completou PIN + Confirmar + Jogar")
    log_info("Retornando para o main.py continuar o monitoramento de desconexão")
    return True