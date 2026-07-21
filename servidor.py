import socket as kct
import threading as thrdn
import time 
from cryptography.fernet import Fernet

#servidor(eu no caso pq sim) 
# --- CONFIGURAÇÃO DE CRIPTOGRAFIA (AES-128) ---

CHAVE_MESTRA = b'nothing'
cipher = Fernet(CHAVE_MESTRA)

LOG_FILE = "chat_log.txt"
PORTA = 5005

def logar(texto):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%H:%M:%S')} | {texto}\n")

clientes = [] 

def broadcast_secure(mensagem_str, origem_conn=None):
    # Encripta a mensagem antes de espalhar
    token = cipher.encrypt(mensagem_str.encode('utf-8'))
    for c in clientes:
        if c != origem_conn:
            try:
                c.send(token)
            except:
                if c in clientes: clientes.remove(c)
     
def RCVmesg(conexao, ender):
    ip_cliente = ender[0]
    print(f"[*] NODE {ip_cliente} CONECTADO.")
    logar(f"Conexão: {ip_cliente}")

    while True:
        try:
            dados = conexao.recv(65536)
            if not dados: break
            
            try:
                # O Servidor descriptografa para logar e mostrar no terminal dele
                msg_descriptografada = cipher.decrypt(dados).decode('utf-8')
                print(f"[{ip_cliente}]: {msg_descriptografada}")
                if msg_descriptografada.startswith("kick "):
                        alvo_ip = msg_descriptografada.replace("kick ", "").strip()
    
    # Procura a conexão que bate com o IP do folgado
                for c in clientes:
                    if c.getpeername()[0] == alvo_ip:
                        c.send(cipher.encrypt(b"VOCE FOI KICKADO.")) # Aviso final
                        c.close() # Mata o link físico
                        clientes.remove(c) # Tira da lista de broadcast
                        print(f"[*] ALVO {alvo_ip} ELIMINADO DA CONEXÃO.")
                        break
                    
                    
                # Retransmite de forma segura para os outros tontos
                broadcast_secure(f"{ip_cliente}: {msg_descriptografada}", conexao)
            except:
                print(f"[!] DROP: Pacote corrompido ou sem chave de {ip_cliente}")
                continue
                
        except: break

    if conexao in clientes: clientes.remove(conexao)
    print(f"[!] NODE {ip_cliente} OFFLINE.")

  
    

def main():
    meu_soquete = kct.socket(kct.AF_INET, kct.SOCK_STREAM)
    meu_soquete.setsockopt(kct.SOL_SOCKET, kct.SO_REUSEADDR, 1)

    try:
        meu_soquete.bind(('0.0.0.0', PORTA))
        meu_soquete.listen()
        print(f"--- K3RN3L HUB ---")
        print(f"[*] BACKBONE ESCUTANDO EM 0.0.0.0:{PORTA}")
        print(f"[*] LOGS SENDO GRAVADOS EM: {LOG_FILE}")
    except Exception as e:
        print(f"[!] ERRO AO INICIAR HUB: {e}")
        return

    # Thread para o ADMIN falar pelo Terminal do Servidor (opcional)
    def admin_talk():
        while True:
            msg = input("")
            if msg:
                print(f"[ADMIN]: {msg}")
                broadcast_secure(f"ADMIN: {msg}")
          
    thrdn.Thread(target=admin_talk, daemon=True).start()

    while True:
        try:
            conn, ender = meu_soquete.accept()
            clientes.append(conn)
            thrdn.Thread(target=RCVmesg, args=(conn, ender), daemon=True).start()
        except: break

if __name__ == "__main__":
    main()
