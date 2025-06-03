import os
import shutil
from PIL import Image
from natsort import natsorted
from tqdm import tqdm
from pathlib import Path


def converter_para_pdf(caminho_pasta, nome_pdf, lista_imagens=None):
    """
    Converte imagens de uma pasta em um único PDF.

    :param caminho_pasta: Path ou str, caminho da pasta com as imagens.
    :param nome_pdf: str, nome do PDF de saída.
    :param lista_imagens: opcional, lista de caminhos das imagens já filtradas e ordenadas.
    """
    caminho_pasta = Path(caminho_pasta)

    # Se não fornecer a lista, busca as imagens na pasta
    if lista_imagens is None:
        extensoes_validas = (".png", ".jpg", ".jpeg", ".bmp")
        arquivos = [
            f
            for f in os.listdir(caminho_pasta)
            if f.lower().endswith(extensoes_validas)
        ]
        arquivos_ordenados = natsorted(arquivos)
        caminhos_imagens = [caminho_pasta / arquivo for arquivo in arquivos_ordenados]
    else:
        caminhos_imagens = lista_imagens

    # Abrir imagens
    imagens = [
        Image.open(caminho).convert("RGB")
        for caminho in tqdm(caminhos_imagens, desc="Convertendo imagens para PDF")
    ]

    download_path = caminho_pasta.parent / "PDFs"
    download_path.mkdir(parents=True, exist_ok=True)

    if imagens:
        pdf_path = download_path / f"{nome_pdf}.pdf"
        imagens[0].save(pdf_path, save_all=True, append_images=imagens[1:])
        print(f"PDF salvo em: {pdf_path}")

        # Remover imagens
        for caminho in caminhos_imagens:
            try:
                os.remove(caminho)
            except Exception as e:
                print(f"Erro ao remover {caminho}: {e}")

        # Remover pasta, se quiser
        try:
            shutil.rmtree(caminho_pasta)
        except Exception as e:
            print(f"Erro ao remover pasta {caminho_pasta}: {e}")

    else:
        print("Nenhuma imagem válida encontrada na pasta.")
