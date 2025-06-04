#!/usr/bin/env python3
"""
Arquivo de teste para executar apenas a digitação do PIN (Passo 3)
sem prosseguir para os passos seguintes.

Baseado na função iniciar_processo_login_completo do funcoes.py
"""

import os
import time
from funcoes import (
    log_info, 
    log_error, 
    log_aviso,
    procurar_e_interagir_imagem,
    digitar_pin_numerico
)

# Inicializa o interception se disponível
try:
    import interception
    log_info("Inicializando Interception...")
    interception.auto_capture_devices(keyboard=True, mouse=True)
    log_info("Interception inicializado com sucesso!")
except ImportError:
    log_aviso("Interception não disponível. Usando PyAutoGUI como fallback.")
except Exception as e:
    log_error(f"Erro ao inicializar Interception: {e}")
    log_aviso("Usando PyAutoGUI como fallback.")

def teste_pin_apenas(pin, pasta_imagens_pin="", confianca_geral=0.8):
    """
    Testa apenas a digitação do PIN, incluindo:
    - Aguardar avatar_pin.png aparecer
    - Aguardar 2 segundos
    - Digitar o PIN
    - NÃO prosseguir para confirmação pós-PIN
    """
    log_info("=== TESTE: DIGITAÇÃO DO PIN APENAS ===")
    
    try:
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
            log_error("Falha ao digitar o PIN.")
            return False
        
        log_info("=== PIN DIGITADO COM SUCESSO! ===")
        log_info("NOTA: Este teste para aqui e NÃO prossegue para o Passo 4 (confirmação pós-PIN)")
        return True
        
    except Exception as e:
        log_error(f"Erro inesperado no teste do PIN: {e}")
        return False

def main():
    """Função principal do teste"""
    log_info("Iniciando teste de digitação do PIN...")
    
    # === CONFIGURAÇÕES DO TESTE ===
    PIN = "1234"  # PIN a ser digitado
    PASTA_IMAGENS_PIN = ""  # Pasta onde estão as imagens dos números (deixe vazio se estão na raiz)
    CONFIANCA_GERAL = 0.8  # Confiança para detecção de imagens
    TESTAR_JOGAR = False  # Se True, testa também o clique no botão "Jogar" após o PIN
    
    log_info("Configurações do teste:")
    log_info(f"  PIN: {'*' * len(PIN)}")
    log_info(f"  Pasta de imagens: {PASTA_IMAGENS_PIN if PASTA_IMAGENS_PIN else 'Diretório atual'}")
    log_info(f"  Confiança: {CONFIANCA_GERAL}")
    log_info(f"  Testar botão Jogar: {'✅ SIM' if TESTAR_JOGAR else '❌ NÃO (apenas PIN)'}")
    
    # Verifica se as imagens necessárias existem
    arquivos_necessarios = ['avatar_pin.png']
    for i in range(10):
        arquivos_necessarios.append(f"{i}.png")
    arquivos_necessarios.append("confirmar.png")
    
    # Adiciona jogar.png se for testar essa funcionalidade
    if TESTAR_JOGAR:
        arquivos_necessarios.append("jogar.png")
    
    arquivos_faltando = []
    for arquivo in arquivos_necessarios:
        caminho = os.path.join(PASTA_IMAGENS_PIN, arquivo) if PASTA_IMAGENS_PIN else arquivo
        if not os.path.exists(caminho):
            arquivos_faltando.append(arquivo)
    
    if arquivos_faltando:
        log_aviso(f"Arquivos não encontrados: {', '.join(arquivos_faltando)}")
        if TESTAR_JOGAR and "jogar.png" in arquivos_faltando:
            log_aviso("ATENÇÃO: jogar.png não encontrado - o teste do botão Jogar falhará")
        log_aviso("O teste pode falhar se essas imagens forem necessárias.")
    else:
        log_info("Todas as imagens necessárias foram encontradas!")
    
    if TESTAR_JOGAR:
        log_info("MODO COMPLETO: Este teste executará PIN + Confirmar + Jogar")
        log_info("NOTA: O teste incluirá o clique no botão 'Jogar' após inserir o PIN")
    else:
        log_info("MODO APENAS PIN: Este teste para após inserir o PIN (não clica em Jogar)")
        log_info("NOTA: Para testar também o botão Jogar, altere TESTAR_JOGAR = True")
    
    # Executa o teste
    log_info("\n" + "="*50)
    log_info("INICIANDO TESTE DO PIN EM 3 SEGUNDOS...")
    log_info("Pressione Ctrl+C para cancelar")
    log_info("="*50)
    
    try:
        for i in range(3, 0, -1):
            log_info(f"Iniciando em {i}...")
            time.sleep(1)
        
        resultado = teste_pin_apenas(PIN, PASTA_IMAGENS_PIN, CONFIANCA_GERAL)
        
        if resultado:
            log_info("\n" + "="*50)
            log_info("✅ TESTE CONCLUÍDO COM SUCESSO!")
            log_info("="*50)
        else:
            log_error("\n" + "="*50)
            log_error("❌ TESTE FALHOU!")
            log_error("="*50)
            
    except KeyboardInterrupt:
        log_aviso("\n" + "="*50)
        log_aviso("⚠️  TESTE CANCELADO PELO USUÁRIO")
        log_aviso("="*50)
    except Exception as e:
        log_error("\n" + "="*50)
        log_error(f"❌ ERRO INESPERADO: {e}")
        log_error("="*50)

if __name__ == "__main__":
    main() 