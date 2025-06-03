"""consumir API MangaDex"""

import requests
from baixar_imagem import salvar_imagem
from pathlib import Path
import os
import json

"""BUSCA E PEGA O ID DE TODOS MANGAS COM O NOME"""


def buscar_manga_por_nome(title, filtros=None):

    BASE_URL = "https://api.mangadex.org"

    filters = {
        "title": title,
        "limit": 100,
        "order[relevance]": "desc",
        **(filtros or {}),
    }

    r = requests.get(f"{BASE_URL}/manga", params=filters)
    print(f"{BASE_URL}/manga {filters}")

    manga = r.json()["data"]
    with open("mangas.json", "w", encoding="utf-8") as f:
        json.dump(manga, f, ensure_ascii=False, indent=4)

    retorno = []

    for manga in r.json()["data"]:
        attributes = manga["attributes"]

        titulo_dict = attributes["title"]
        titulo = titulo_dict.get("en") or next(iter(titulo_dict.values()), "Sem título")

        descricao = attributes["description"].get("pt") or attributes[
            "description"
        ].get("en", "Sem descrição")

        tags = [tag["attributes"]["name"]["en"] for tag in attributes["tags"]]

        # Links
        links = attributes.get("links", {})

        # Relationships
        autor = artista = criador = capa = "Desconhecido"

        for rel in manga.get("relationships", []):
            if rel["type"] == "author":
                autor = rel["id"]
            elif rel["type"] == "artist":
                artista = rel["id"]
            elif rel["type"] == "creator":
                criador = rel["id"]
            elif rel["type"] == "cover_art":
                capa = rel["id"]

        retorno.append(
            {
                "id": manga["id"],
                "titulo": titulo,
                "altTitles": attributes.get("altTitles", []),
                "sinopse": descricao,
                "demografia": attributes.get("publicationDemographic", "Indefinido"),
                "status": attributes.get("status", "Indefinido"),
                "ano": attributes.get("year", "Desconhecido"),
                "classificacao": attributes.get("contentRating", "Indefinido"),
                "tags": tags,
                "idioma": attributes.get("originalLanguage", "Desconhecido"),
                "capitulos": attributes.get("lastChapter", "Desconhecido"),
                "links": links,
                "autor": autor,
                "artista": artista,
                "criador": criador,
                "capa": capa,
                "availableTranslatedLanguages": attributes.get(
                    "availableTranslatedLanguages", []
                ),
            }
        )

    return retorno


"""BUSCA OS CAPITULOS DO MANGA PELO ID"""
import requests


def buscar_capitulos_por_id(id):
    BASE_URL = "https://api.mangadex.org"
    # Tenta buscar capítulos em pt-br
    url_nome = f"{BASE_URL}/manga/{id}"
    response_nome = requests.get(url_nome)
    name_data = response_nome.json()
    manga_name = name_data["data"]["attributes"]["title"].get("pt") or name_data[
        "data"
    ]["attributes"]["title"].get("en", "Sem título")

    url = f"{BASE_URL}/manga/{id}/feed?limit=100&contentRating[]=safe&contentRating[]=suggestive&contentRating[]=erotica&order[chapter]=asc"
    response = requests.get(url)

    if response.ok:
        data = response.json()

        if not data.get("data"):  # lista vazia -> tenta sem filtro
            url = f"{BASE_URL}/manga/{id}/feed?limit=100&contentRating[]=safe&contentRating[]=suggestive&contentRating[]=erotica&contentRating[]=pornographic&order[chapter]=asc"
            response = requests.get(url)
            if response.ok:
                data = response.json()
            else:
                return []
    else:
        url = f"{BASE_URL}/manga/{id}/feed?limit=100&contentRating[]=safe&contentRating[]=suggestive&contentRating[]=erotica&contentRating[]=pornographic&order[chapter]=asc"
        response = requests.get(url)

        if response.ok:
            data = response.json()

        else:
            return []
    chap_info = []
    for chap in data["data"]:
        cap_num = chap["attributes"]["chapter"]
        try:
            cap_num = float(cap_num)
        except (TypeError, ValueError):
            cap_num = 0
        chap_info.append(
            {
                "id": chap["id"],
                "titulo": chap["attributes"]["title"],
                "capitulo": cap_num,
                "manga": manga_name,
            }
        )

    with open("capitulos.txt", "w", encoding="utf-8") as f:
        for chap in chap_info:
            f.write(f"{chap['id']}\n")
            f.write(f"{chap['titulo']}\n")
            f.write(f"{chap['capitulo']}\n")

    return chap_info


"""BUSCAR PAGINAS PELO ID DO CAPITULO"""


def buscar_paginas(id):

    url = f"https://api.mangadex.org/at-home/server/{id}"

    response = requests.get(url)
    data = response.json()
    BASE_URL = data["baseUrl"]
    manga_hash = data["chapter"]["hash"]
    manga_pages = data["chapter"]["dataSaver"]
    url_imagens = []
    for i, pagina in enumerate(manga_pages):
        url = f"{BASE_URL}/data-saver/{manga_hash}/{pagina}"
        url_imagens.append(
            {
                "pagina": i,
                "url": url,
            }
        )
    return url_imagens
