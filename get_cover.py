import requests


def get_manga_cover(manga_id, cover_id):
    url = f"https://api.mangadex.org/cover?limit=1&manga[]={manga_id}&ids[]={cover_id}&order[createdAt]=asc&order[updatedAt]=asc&includes[]=manga"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        cover_url = data["data"][0]["attributes"]["fileName"]
        complete_url = f"https://uploads.mangadex.org/covers/{manga_id}/{cover_url}"
        return complete_url
    return None


if __name__ == "__main__":
    manga_id = "20247328-6d87-4593-8634-776a443e47c3"  # Exemplo de ID do mangá
    cover_id = "3d217f59-ba4a-4bf8-9b46-02026080a4cb"  # Exemplo de ID da capa
    cover_url = get_manga_cover(manga_id, cover_id)
    if cover_url:
        print(f"Capa do mangá: {cover_url}")
    else:
        print("Capa não encontrada.")
