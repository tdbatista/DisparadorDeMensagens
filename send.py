"""
send.py
BY THIAGO N S B ALMEIDA


Requisitos:
- Python 3.8+
- selenium, pandas
- Chrome + ChromeDriver (versão compatível)
- Um arquivo opcional "contacts.csv" com coluna "Name" (opcional) ou
  o script tentará usar os chats visíveis no WhatsApp Web.
- Uma imagem em CAMINHO_IMAGEM (caminho absoluto recomendado).

Uso:
1) Ajuste CHROMEDRIVER_PATH e CAMINHO_IMAGEM.
2) Rode: python send.py
3) Escaneie o QR code no WhatsApp Web quando o navegador abrir.
4) Aguarde o script enviar as imagens. Verifique 'sent_log.csv' para históricos.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

import time
import os
import pandas as pd
from datetime import datetime

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



# ---------------- CONFIGURAÇÃO ----------------
CHROMEDRIVER_PATH = r"C:/chromedriver/chromedriver.exe"   # ajuste conforme seu sistema
CAMINHO_IMAGEM = r"C:/promobotija85.png"               # imagem a enviar (use caminho absoluto)
CONTACTS_CSV = "contacts.csv"                             # arquivo CSV do google
SENT_LOG = "sent_log.csv"                                 # log dos envios para evitar duplicados

# Delays (ajuste se necessário)
DELAY_AFTER_SEARCH = 2
DELAY_AFTER_OPEN_CHAT = 2
DELAY_BEFORE_ATTACH = 1
DELAY_AFTER_ATTACH = 3
DELAY_BETWEEN_CONTACTS = 2


MAX_SENDS_PER_DAY = 25
INTERVALDO_DE_DIAS = 30
INTERVALO_ENTRE_DISPAROS = 5
DURACAO_INTERVALO = 300
# ------------------------------------------------

def load_contacts_csv(path):
    if not os.path.exists(path):
        print(f"Não foi localizado o arquivo {CONTACTS_CSV}.")
        return None
    try:
        df = pd.read_csv(path, dtype=str)
        if 'Phone 1 - Value' in df.columns:
            names = df['Phone 1 - Value'].dropna().astype(str).tolist()
            return names
        else:
            # tenta colunas alternativas
            if 'First Name' in df.columns:
                return df['First Name'].dropna().astype(str).tolist()
            return None
    except Exception as e:
        print("Erro lendo CSV:", e)
        return None

def load_sent_log(path):
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            return set(df['Contact'].astype(str).tolist()), df
        except Exception:
            return set(), pd.DataFrame(columns=['Contact','When','Status'])
    else:
        return set(), pd.DataFrame(columns=['Contact','When','Status'])

def append_sent_log(path, df, contact, status="SENT"):
    new_row = {'Contact': contact, 'When': datetime.now().isoformat(timespec='seconds'), 'Status': status}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    df.to_csv(path, index=False)
    return df

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

def send_image_to_current_chat(driver, image_path):
    try:
        wait = WebDriverWait(driver, 20)

         # ✅ 1. Clicar no botão “Anexar”
        anexar = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and @aria-label='Anexar']")))
        anexar.click()
        time.sleep(0.5)  # pequeno delay para o submenu abrir

        # ✅ 2. Localizar o campo <input type="file"> dentro do menu "Fotos e vídeos"
        input_file = wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                "//li//span[contains(text(), 'Fotos e vídeos')]/following-sibling::input[@type='file']"
            ))
        )

        # Verifica se a imagem existe
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

        # ✅ 3. Envia o caminho da imagem direto no input (não precisa clicar)
        input_file.send_keys(os.path.abspath(image_path))
        time.sleep(2)  # aguarda carregar a prévia da imagem

        # ✅ 4. Clicar no botão de enviar (aviãozinho)
        # ✅ 4. Clicar no botão de enviar (aviãozinho atualizado)
        botao_enviar = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//div[@role='button' and @aria-label='Enviar' and not(@aria-disabled='true')]"
            ))
        )
        botao_enviar.click()


        print("📸 Imagem enviada com sucesso!")
        return True
    except Exception as e:
        print("Erro ao enviar imagem:", e)
        return False


def open_chat_by_search(driver, contact_name):
    """Usa a caixa de busca para abrir conversa pelo nome do contato."""
    try:
        # caixa de busca - observa que o data-tab pode variar; este xpath funciona em muitas versões
        search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
        # limpa
        search_box.click()
        
        time.sleep(0.3)
        search_box.send_keys(Keys.CONTROL, 'a')  # Seleciona tudo
        time.sleep(0.1)
        search_box.send_keys(Keys.BACKSPACE)     # Apaga
        time.sleep(0.3)
        time.sleep(0.5)
        search_box.send_keys(contact_name)
        time.sleep(DELAY_AFTER_SEARCH)
        # tenta abrir o primeiro resultado (ENTER)
        search_box.send_keys(Keys.ENTER)

        time.sleep(DELAY_AFTER_OPEN_CHAT)
        return True
    except Exception as e:
        print(f"Erro buscando contato {contact_name}:", e)
        return False

def get_visible_chats(driver):
    """
    Tenta obter uma lista de nomes de conversas visíveis na barra lateral (pane-side).
    Atenção: seletores podem variar com atualizações do WhatsApp Web.
    """
    names = []
    try:
        pane = driver.find_element(By.ID, "pane-side")
        # cada chat costuma ser um link com role="link"; selecionamos spans com dir="auto" que contêm o nome
        chat_elements = pane.find_elements(By.XPATH, './/div[contains(@role,"link")]')
        for chat in chat_elements:
            try:
                # nome do contato/chat (muitas vezes dentro de uma span com dir="auto")
                name_elem = chat.find_element(By.XPATH, './/span[@dir="auto"]')
                name = name_elem.text.strip()
                if name:
                    names.append(name)
            except Exception:
                continue
    except Exception as e:
        print("Não foi possível listar chats visíveis:", e)
    # eliminar duplicados preservando ordem
    seen = set()
    filtered = []
    for n in names:
        if n not in seen:
            filtered.append(n)
            seen.add(n)
    return filtered

def main():
    if not os.path.exists(CAMINHO_IMAGEM):
        print("Imagem não encontrada em:", CAMINHO_IMAGEM)
        return

    # carrega contatos do CSV se existir
    contacts_from_csv = load_contacts_csv(CONTACTS_CSV)
    sent_set, sent_df = load_sent_log(SENT_LOG)

    options = webdriver.ChromeOptions()
    options.add_argument(r"user-data-dir=C:\whatsapp_session")  # pasta persistente
    
    # inicializa webdriver
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://web.whatsapp.com/")
    print("Aguardando login no WhatsApp Web. Escaneie o QR code.")
    input("Após escanear e estar logado, pressione ENTER aqui...")

    time.sleep(3)
    
    

    # se CSV fornecido, usa isso; caso contrário pega chats visíveis
    if contacts_from_csv:
        contacts = contacts_from_csv
        print(f"Usando {len(contacts)} contatos do arquivo {CONTACTS_CSV}.")
    else:
        print(f"Nenhum {CONTACTS_CSV} encontrado. Lendo chats visíveis na barra lateral...")
        time.sleep(2)
        contacts = get_visible_chats(driver)
        print(f"Encontrados {len(contacts)} chats visíveis. Eles serão usados.")
    sends = 0
    for contact in contacts:
        if sends >= MAX_SENDS_PER_DAY:
            break
        # pular se já enviado
        linha = sent_df.loc[sent_df['Contact']==contact]
        if not linha.empty:
            #SE O STATUS FOR DE ERRO
            status = linha.iloc[0]['Status']
            if status!="SENT":
                print(f"Pulando {contact} (já enviado anteriormente).")
                continue
            #SE FOR MAIS DE DIAS
            when = linha.iloc[0]['When']
            if not pd.isna(when):
                hoje = datetime.now()
                when = pd.to_datetime(when, errors='coerce')
                dias = (hoje - when).days

                if dias < INTERVALDO_DE_DIAS:
                    print(f"Pulando {contact} (enviado há {dias} dias).")
                    continue
                else:
                    print(f"{contact} foi enviado há {dias} dias, reenviando.")

        
        
        print(f"Tentando abrir conversa: {contact}")
        ok = open_chat_by_search(driver, contact)
        if not ok:
            print(f"Falha ao abrir {contact}. Registrando como ERROR.")
            sent_df = append_sent_log(SENT_LOG, sent_df, contact, status="ERROR_OPEN_CHAT")
            sent_set.add(str(contact))
            continue

        # Tenta enviar a imagem
        sent_ok = send_image_to_current_chat(driver, CAMINHO_IMAGEM)
        if sent_ok:
            print(f"Imagem enviada para {contact}.")
            sent_df = append_sent_log(SENT_LOG, sent_df, contact, status="SENT")
            sent_set.add(str(contact))
            sends+=1
            # para o zuck não dar block ele da uma pausa
            if sends % INTERVALO_ENTRE_DISPAROS==0:
                time.sleep(DURACAO_INTERVALO)
                print(f"Pausa dos disparos de {DURACAO_INTERVALO} segundos.")
        else:
            print(f"Falha ao enviar imagem para {contact}. Registrando erro.")
            sent_df = append_sent_log(SENT_LOG, sent_df, contact, status="ERROR_SEND")
            sent_set.add(str(contact))

        time.sleep(DELAY_BETWEEN_CONTACTS)

    print("Processo finalizado.")
    driver.quit()

if __name__ == "__main__":
    main()
