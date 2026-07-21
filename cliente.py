import socket as kct
import threading as thrnd
import time
from cryptography.fernet import Fernet

# --- CONFIGURAÇÃO DE CRIPTOGRAFIA ---
CHAVE_MESTRA = b'nothing'
cipher = Fernet(CHAVE_MESTRA)

# IP do seu Servidor (Mude aqui se precisar)
HOST = "100.xxx.xx.xx" 
PORT = 5005

meu_soquete = kct.socket(kct.AF_INET, kct.SOCK_STREAM)

def RCVmesg():
    while True:
        try:
            dados = meu_soquete.recv(4096)
            if not dados: break
            
            try:
                # DESCRIPTOGRAFA 
                mensagem = cipher.decrypt(dados).decode('utf-8').strip()
            except:
                # SE VIER LIXO, MOSTRA O BRUTO (DEBUG)
                mensagem = f"RAW_ERROR: {dados.decode('utf-8', errors='ignore')}"

            print(f"\n[RECEBIDO]: {mensagem}\n>>> ", end="")
        except:
            print("\n[!] CONEXÃO PERDIDA COM O HUB.")
            break

def main():
    try:
        print(f"[*] TENTANDO HANDSHAKE COM {HOST}...")
        meu_soquete.connect((HOST, PORT))
        print("[+] CONECTOU")
        
        # Inicia a thread de escuta
        thrnd.Thread(target=RCVmesg, daemon=True).start()

        while True:
            msg = input(">>> ")
            if msg.lower() == 'exit': break
            
            # ENCRIPTANDO E ENVIANDO 
            token = cipher.encrypt(msg.encode('utf-8'))
            meu_soquete.send(token)
            time.sleep(0.1) # Delay para evitar sticky packets

    except Exception as e:
        print(f"[!] ERRO CRÍTICO: {e}")
    finally:
        meu_soquete.close()

if __name__ == "__main__":
    main()
