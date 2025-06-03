import requests
import os

session = requests.Session()


def salvar_imagem(url_imagem, nome_arquivo):
    if os.path.exists(nome_arquivo):
        return
    try:
        resposta = session.get(url_imagem, timeout=10)
        resposta.raise_for_status()
        with open(nome_arquivo, "wb") as f:
            f.write(resposta.content)
    except Exception as e:
        print(f"[✕] Erro ao baixar {url_imagem}: {e}")
