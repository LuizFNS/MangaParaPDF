from bs4 import BeautifulSoup
import requests
import time
from pathlib import Path
import os


class Sites:
    def __init__(self, site_name, site_url):
        self.site_name = site_name
        self.site_url = site_url


class MangaLivre(Sites):
    def __init__(self):
        super().__init__("Manga Livre", "https://mangalivre.blog")
        self.base_url = "https://mangalivre.blog/manga/"
        self.search_url = "https://mangalivre.blog/?s="
        self.chapter_url_template = "https://mangalivre.blog/manga/{}-capitulo-{}"
        self.search_class = "manga-card-link"  # classe usada nos resultados de busca
        self.tag = "img"
        self.class_name = "chapter-image"  # classe usada para as imagens dos capítulos

    def get_chapter_url(self, manga_slug, chapter_number):
        return self.chapter_url_template.format(manga_slug, chapter_number)

    def buscar_mangas(self, termo_busca):
        """Realiza a busca e retorna uma lista de tuplas (nome_formatado, slug, url)"""
        termo_busca = termo_busca.strip().replace(" ", "+")
        url = self.search_url + termo_busca
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        resultados = []
        for a in soup.find_all("a", class_=self.search_class):
            href = a.get("href")
            if href:
                slug = href.strip("/").split("/")[-1]
                titulo = slug.replace("-", " ").title()
                resultados.append({"titulo": titulo, "slug": slug, "url": href})
        return resultados

    def buscar_capitulos(self, slug, capitulo_inicial=None, capitulo_final=None):
        url = f"{self.base_url}{slug}/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        capitulos = []

        for cap in soup.find_all("li", class_="chapter-item"):
            a = cap.find("a")
            print(f"VAR: a => {a}")
            if not a:
                continue

            cap_url = a.get("href")
            print(f"VAR: cap_url => {cap_url}")
            cap_text = (
                a.text.strip()
                .lower()
                .replace("capítulo", "")
                .replace("capitulo", "")
                .strip()
            )
            print(f"VAR: cap_text => {cap_text}")

            try:
                cap_num = float(cap_text)
            except ValueError:
                cap_num = None  # pode ser extra, especial etc.

            # Se filtros forem fornecidos
            if cap_num is not None:
                if capitulo_inicial and cap_num < capitulo_inicial:
                    continue
                if capitulo_final and cap_num > capitulo_final:
                    continue

            capitulos.append(
                {
                    "id": cap_url.strip("/").split("/")[-1],  # último trecho da URL
                    "url": cap_url,
                    "capitulo": cap_num,
                }
            )
        print(f"VAR: capitulos => {capitulos}")
        # A ordem pode vir invertida no site
        return list(reversed(capitulos))

    def buscar_capitulo_2(self, slug, capitulo_inicial=None, capitulo_final=None):
        capitulo_inicial = int(capitulo_inicial) if capitulo_inicial else 1
        capitulo_final = int(capitulo_final) if capitulo_final else 1
        print(
            f"VAR: slug => {slug}\nVAR: capitulo_inicial => {capitulo_inicial}\nVAR: capitulo_final => {capitulo_final}"
        )
        base_url = f"https://mangalivre.blog/capitulo/{slug}"
        capitulos = []
        for i in range(capitulo_inicial, capitulo_final):
            url = f"{base_url}-capitulo-{i}"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            capitulos.append(
                {
                    "id": url.strip("/").split("/")[-1],  # último trecho da URL
                    "url": url,
                    "capitulo": float(i),
                }
            )
            print(f"VAR: capitulos => {capitulos}")
            # A ordem pode vir invertida no site
        return list(reversed(capitulos))

    def quantidade_capitulos(self, manga, site):
        if site.startswith("https://mangalivre.blog"):
            url = f"https://mangalivre.blog/manga/{manga}/"

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        resposta = []

        for i, nome_capitulo in enumerate(
            soup.find_all("span", class_="chapter-number")
        ):
            resposta.append(nome_capitulo)
        return len(resposta)

    def baixar_capitulo(self, slug, qtd_cap, cap_inicio, cap_fim):
        manga = slug
        cap_inicio = input(
            "\nDigite o capitulo para iniciar o download!\n[Deixe em branco para o primeiro disponivel]:\n-> "
        )
        cap_fim = input(
            f"\nDigite o ultimo capitulo para download!\n[Deixe em branco para ultimo disponivel ({quantidade_capitulos(manga)})]:\n-> "
        )
        if cap_inicio == "":
            cap_inicio = 1
        for i in range(int(cap_inicio), int(qtd_cap) + 1):
            url_capitulo = f"https://mangalivre.blog/capitulo/{manga}-capitulo-{i}"
            html_capitulo = requests.get(url_capitulo)
            soup_capitulo = BeautifulSoup(html_capitulo.text, "html.parser")
            caminho_base = Path(str(manga))
            nome_pasta = caminho_base / f"Capitulo {i}"
            nome_pasta.mkdir(parents=True, exist_ok=True)

            for i, imagem in enumerate(
                soup_capitulo.find_all("img", class_="chapter-image")
            ):
                url_imagem = imagem.get("src")

                if url_imagem:
                    nome_arquivo = os.path.join(nome_pasta, f"pagina_{i+1}.jpg")
                    salvar_imagem = {
                        "url_imagem": url_imagem,
                        "nome_arquivo": nome_arquivo,
                    }
        return salvar_imagem


if __name__ == "__main__":
    manga_livre = MangaLivre()
    termo_busca = "One Piece"
    resultados = manga_livre.buscar_mangas(termo_busca)
    links = []
    for nome, slug, url in resultados:
        links.append({"Nome": nome, "Slug": slug, "URL": url})
