import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO
from mangadex import buscar_manga_por_nome, buscar_capitulos_por_id, buscar_paginas
from baixar_imagem import salvar_imagem
from converter_pdf import converter_para_pdf
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import threading
import requests
from bs4 import BeautifulSoup

from get_cover import get_manga_cover
from sites import MangaLivre

ml = MangaLivre()

dark_bg = "#121212"
text_color = "#E0E0E0"
button_bg = "#333333"
button_hover_bg = "#555555"
entry_bg = "#222222"
border_color = "#444444"


class MangaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Manga Downloader")
        # Estilos de cores para o tema escuro

        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.resizable(False, False)
        root.config(bg=dark_bg)
        style = ttk.Style(root)
        style.theme_use("clam")  # Tema que aceita bem customização

        style.configure(
            "dark.Horizontal.TProgressbar",
            troughcolor="#222222",  # fundo da barra
            background="#3A3A5E",  # cor da parte preenchida
            bordercolor="#444444",
            lightcolor="#5A5AFF",
            darkcolor="#2A2A4E",
        )

        self.filtros = {}
        self.mangas = []

        self.label_pesquisa = tk.Label(
            root, text="Pesquisar", bg=dark_bg, fg=text_color
        )
        self.label_pesquisa.grid(row=0, column=0, sticky="w")

        self.entry_pesquisa = tk.Entry(
            root, width=50, bg=entry_bg, fg=text_color, borderwidth=2, relief="solid"
        )
        self.entry_pesquisa.grid(row=1, column=0, padx=10, sticky="ew", columnspan=3)

        self.btn_buscar = tk.Button(
            root, text="Buscar", command=self.buscar_manga, bg=button_bg, fg=text_color
        )
        self.btn_buscar.grid(row=2, column=1, sticky="ew", pady=5)

        self.btn_buscar_ml = tk.Button(
            root,
            text="Buscar [ML]",
            command=self.buscar_manga_ml,
            bg=button_bg,
            fg=text_color,
        )
        self.btn_buscar_ml.grid(row=2, column=2, sticky="ew", pady=5, padx=10)

        self.btn_filtros = tk.Button(
            root,
            text="Filtros",
            command=self.abrir_filtros,
            bg=button_bg,
            fg=text_color,
        )
        self.btn_filtros.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        self.lista_resultados = tk.Listbox(
            root,
            width=80,
            bg=entry_bg,
            fg=text_color,
            selectbackground=button_hover_bg,
            selectforeground="#FFFFFF",
            highlightthickness=1,
            highlightbackground="#444444",
            relief="flat",
        )
        self.lista_resultados.grid(row=3, column=0, columnspan=3, padx=10)

        self.btn_baixar = tk.Button(
            root,
            text="Info Manga",
            command=self.abrir_infos,
            bg=button_bg,
            fg=text_color,
        )
        self.btn_baixar.grid(
            row=4, column=0, sticky="ew", padx=10, pady=5, columnspan=2
        )

        self.btn_baixar_ml = tk.Button(
            root,
            text="Baixar [ML]",
            command=self.baixar_manga_ml,
            bg=button_bg,
            fg=text_color,
        )
        self.btn_baixar_ml.grid(row=4, column=2, sticky="ew", padx=10, pady=5)

        self.progress = ttk.Progressbar(
            root,
            orient="horizontal",
            length=400,
            mode="determinate",
            style="dark.Horizontal.TProgressbar",
        )
        self.progress.grid(row=5, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

    def buscar_manga(self):
        self.progress["value"] = 0
        titulo = self.entry_pesquisa.get()
        self.lista_resultados.delete(0, tk.END)

        try:
            self.mangas = buscar_manga_por_nome(titulo, filtros=self.filtros)
            print(self.filtros)
            for i, manga in enumerate(self.mangas):
                nome = manga.get("titulo", "Sem nome")
                self.lista_resultados.insert(tk.END, f"[{i+1}] {nome}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar mangá: {e}")

    def abrir_infos(self):
        ttk.Style().theme_use("clam")  # Garante que o tema esteja configurado
        sel = self.lista_resultados.curselection()

        if not sel:
            messagebox.showwarning(
                "Aviso", "Selecione um mangá para ver as informações."
            )
            return
        index = sel[0]
        manga = self.mangas[index]

        infos = {
            "Título": manga.get("titulo", "Sem título"),
            "ID": manga.get("id", "Desconhecido"),
            "Capítulos": manga.get("capitulos", "Desconhecido"),
            "Status": manga.get("status", "Desconhecido"),
            "Demografia": manga.get("demografia", "Desconhecido"),
            "Idioma": manga.get("idioma", "Desconhecido"),
            "Classificação": manga.get("classificacao", "Desconhecido"),
            "Tags": manga.get("tags", "Desconhecido"),
            "Autor": manga.get("autor", "Desconhecido"),
            "Artista": manga.get("artista", "Desconhecido"),
            "Criador": manga.get("criador", "Desconhecido"),
            "Sinopse": manga.get("sinopse", "Desconhecido"),
            "Capa": manga.get("capa", "Desconhecido"),
            "Links": manga.get("links", "Desconhecido"),
        }
        # Paleta dark mode
        dark_bg = "#1E1E2F"  # fundo geral
        dark_frame_bg = "#2C2C44"  # fundo frame interno
        text_primary = "#E0E0F0"  # texto normal
        text_secondary = "#A0A0B0"  # texto labels
        accent_color = "#5C7AEA"  # azul para destaque
        separator_color = "#44475a"  # cor do separador

        janela = tk.Toplevel(self.root)
        janela.title("Informações do Mangá")
        janela.geometry("520x450")
        janela.configure(bg=dark_bg)
        janela.resizable(False, False)

        # Scrollable frame setup
        canvas = tk.Canvas(janela, bg=dark_bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(janela, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, style="Dark.TFrame")

        scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        # Definindo estilos customizados
        style = ttk.Style(janela)
        style.configure("Dark.TFrame", background=dark_frame_bg)
        style.configure(
            "Dark.TLabel",
            background=dark_frame_bg,
            foreground=text_primary,
            font=("Segoe UI", 9),
        )
        style.configure(
            "DarkBold.TLabel",
            background=dark_frame_bg,
            foreground=accent_color,
            font=("Segoe UI", 12, "bold"),
        )
        style.configure(
            "DarkKey.TLabel",
            background=dark_frame_bg,
            foreground=text_secondary,
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "DarkItalic.TLabel",
            background=dark_frame_bg,
            foreground=text_primary,
            font=("Segoe UI", 9, "italic"),
        )
        style.configure("Dark.TSeparator", background=separator_color)

        # Estilos de fonte
        titulo_font = ("Segoe UI", 14, "bold")
        label_font = ("Segoe UI", 11, "bold")
        valor_font = ("Segoe UI", 11)
        sinopse_font = ("Segoe UI", 10, "italic")

        # Título no topo
        label_titulo = ttk.Label(
            scroll_frame, text=infos["Título"], style="DarkBold.TLabel"
        )
        label_titulo.grid(
            row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10)
        )

        # Linha separadora
        separator1 = ttk.Separator(
            scroll_frame, orient="horizontal", style="Dark.TSeparator"
        )
        separator1.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=1)

        # Campos principais (exclui Sinopse, Capa e Links para tratar separado)
        campos_principais = [
            "ID",
            "Capítulos",
            "Status",
            "Demografia",
            "Idioma",
            "Classificação",
            "Tags",
            "Autor",
            "Artista",
            "Criador",
        ]

        for i, chave in enumerate(campos_principais, start=2):
            valor = infos[chave]
            if isinstance(valor, list):
                valor = ", ".join(str(x) for x in valor)
            elif isinstance(valor, dict):
                valor = ", ".join(f"{k}: {v}" for k, v in valor.items())

            label_chave = ttk.Label(
                scroll_frame, text=f"{chave}:", style="DarkKey.TLabel"
            )
            label_chave.grid(row=i, column=0, sticky="nw", padx=15, pady=6)

            text_valor = tk.Text(
                scroll_frame,
                width=30,
                height=2,
                wrap="word",
                borderwidth=0,
                background=dark_bg,
                foreground="#DDDDDD",
                font=valor_font,
            )
            text_valor.insert("1.0", str(valor))
            text_valor.config(state="disabled")
            text_valor.grid(row=i, column=1, sticky="nw", padx=10, pady=6)

        # Sinopse separada com maior destaque e espaço
        sinopse_idx = len(campos_principais) + 3
        separator2 = ttk.Separator(
            scroll_frame, orient="horizontal", style="Dark.TSeparator"
        )
        separator2.grid(
            row=sinopse_idx - 1,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=10,
            pady=(15, 10),
        )

        ttk.Label(scroll_frame, text="Sinopse:", style="DarkKey.TLabel").grid(
            row=sinopse_idx, column=0, sticky="nw", padx=15, pady=(0, 5)
        )
        sinopse_text = tk.Text(
            scroll_frame,
            width=30,
            height=10,
            wrap="word",
            borderwidth=0,
            background=dark_bg,
            foreground="#DDDDDD",
            font=sinopse_font,
        )
        sinopse_text.insert("1.0", infos["Sinopse"])
        sinopse_text.config(state="disabled")
        sinopse_text.grid(row=sinopse_idx, column=1, sticky="nw", padx=10, pady=(0, 15))

        # Capa
        capa_idx = sinopse_idx + 1
        ttk.Separator(scroll_frame, orient="horizontal", style="Dark.TSeparator").grid(
            row=capa_idx - 1, column=0, columnspan=2, sticky="ew", padx=10, pady=1
        )
        capa_url = get_manga_cover(manga["id"], infos["Capa"])

        if capa_url:
            try:
                response = requests.get(capa_url)
                imagem = Image.open(BytesIO(response.content))
                imagem = imagem.resize((200, 300))  # Ajusta o tamanho conforme desejar

                imagem_tk = ImageTk.PhotoImage(imagem)

                # Mantém a referência para não ser coletado
                if not hasattr(self, "imagens_refs"):
                    self.imagens_refs = []
                self.imagens_refs.append(imagem_tk)

                capa_label = tk.Label(scroll_frame, image=imagem_tk, bg=dark_bg)
                capa_label.grid(
                    row=capa_idx + 1, column=0, columnspan=2, pady=30, sticky="nsew"
                )

            except Exception as e:
                print(f"Erro ao carregar imagem da capa: {e}")
        ttk.Label(scroll_frame, text="Capa:", style="DarkKey.TLabel").grid(
            row=capa_idx, column=0, sticky="nw", padx=15, pady=6
        )
        capa_text = tk.Text(
            scroll_frame,
            width=30,
            height=2,
            wrap="word",
            borderwidth=0,
            background=dark_bg,
            foreground="#DDDDDD",
            font=valor_font,
        )
        capa_text.insert("1.0", infos["Capa"])
        capa_text.config(state="disabled")
        capa_text.grid(row=capa_idx, column=1, sticky="nw", padx=5, pady=5)

        # Links
        links_idx = capa_idx + 1
        ttk.Separator(scroll_frame, orient="horizontal", style="Dark.TSeparator").grid(
            row=links_idx - 1, column=0, columnspan=2, sticky="ew", padx=10, pady=1
        )

        ttk.Label(scroll_frame, text="Links:", style="DarkKey.TLabel").grid(
            row=links_idx, column=0, sticky="nw", padx=15, pady=6
        )
        links_text = tk.Text(
            scroll_frame,
            width=30,
            height=4,
            wrap="word",
            borderwidth=0,
            background=dark_bg,  # Ou a variável/cor que você tá usando no fundo.
            foreground="#DDDDDD",
            font=valor_font,
        )
        links_text.insert("1.0", infos["Links"])
        links_text.config(state="disabled")
        links_text.grid(row=links_idx, column=1, sticky="nw", padx=5, pady=6)

        # Frame fixo para botões, fora do canvas e do scroll_frame
        fixed_frame = ttk.Frame(janela, style="Dark.TFrame")
        fixed_frame.pack(fill="x", side="bottom", padx=5, pady=10)

        btn_baixar = ttk.Button(fixed_frame, text="Baixar", command=self.baixar_manga)
        btn_baixar.pack(side="bottom", expand=True, padx=5, pady=10)

        btn_fechar = ttk.Button(fixed_frame, text="Fechar", command=janela.destroy)
        btn_fechar.pack(side="bottom", expand=True, padx=5, pady=10)

    def abrir_filtros(self):
        janela = tk.Toplevel(self.root)
        janela.title("Filtros")
        janela.geometry("320x490")

        tk.Label(janela, text="Idioma").pack()
        idioma_box = ttk.Combobox(
            janela, values=["pt-br", "en", "ja", "es", "zh", "ko", ""]
        )
        idioma_box.set(self.filtros.get("translatedLanguage[]", ""))
        idioma_box.pack(pady=5)

        tk.Label(janela, text="Status").pack()
        status_box = ttk.Combobox(
            janela, values=["", "ongoing", "completed", "hiatus", "cancelled"]
        )
        status_box.set(self.filtros.get("status[]", ""))
        status_box.pack(pady=5)

        def criar_checkbuttons(titulo, lista, variaveis, filtro_chave):
            frame = tk.Frame(janela)
            frame.pack(pady=5)
            tk.Label(frame, text=titulo).grid(row=0, column=0, columnspan=2)
            for i, item in enumerate(lista):
                selecionado = item in self.filtros.get(filtro_chave, [])
                var = tk.BooleanVar(value=selecionado)
                variaveis[item] = var
                tk.Checkbutton(frame, text=item, variable=var).grid(
                    row=2 + i // 2, column=i % 2, padx=10, sticky="w"
                )

        self.dem_vars = {}
        criar_checkbuttons(
            "Demografia",
            ["shounen", "shoujo", "josei", "seinen"],
            self.dem_vars,
            "publicationDemographic[]",
        )

        self.inc_vars = {}
        criar_checkbuttons(
            "Includes",
            ["manga", "cover_art", "author", "artist", "tag", "creator"],
            self.inc_vars,
            "includes[]",
        )

        self.rating_vars = {}
        criar_checkbuttons(
            "Classificação",
            ["safe", "suggestive", "erotica", "pornographic"],
            self.rating_vars,
            "contentRating[]",
        )

        def aplicar():
            idioma = idioma_box.get().strip()
            status = status_box.get().strip()

            self.filtros = {}
            if idioma:
                self.filtros["translatedLanguage[]"] = idioma
            if status:
                self.filtros["status[]"] = status

            dem = [k for k, v in self.dem_vars.items() if v.get()]
            if dem:
                self.filtros["publicationDemographic[]"] = dem

            inc = [k for k, v in self.inc_vars.items() if v.get()]
            if inc:
                self.filtros["includes[]"] = inc

            rating = [k for k, v in self.rating_vars.items() if v.get()]
            if rating:
                self.filtros["contentRating[]"] = rating

            janela.destroy()

        tk.Button(janela, text="Aplicar", command=aplicar).pack(pady=10)

    def buscar_manga_ml(self):
        titulo = self.entry_pesquisa.get()
        self.lista_resultados.delete(0, tk.END)

        try:
            self.mangas = ml.buscar_mangas(titulo)
            for i, manga in enumerate(self.mangas):
                nome = manga.get("titulo", "Sem nome")
                self.lista_resultados.insert(tk.END, f"[ML][{i+1}] {nome}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar mangá: {e}")

    def baixar_manga_ml(self):
        sel = self.lista_resultados.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um mangá para baixar.")
            return

        index = sel[0]
        manga = self.mangas[index]
        slug = manga["slug"]
        titulo = manga["titulo"]
        caminho_base = Path("downloads") / titulo
        caminho_base.mkdir(parents=True, exist_ok=True)

        total_caps = ml.quantidade_capitulos(slug, ml.site_url)
        entrada = simpledialog.askfloat(
            "Capítulo inicial", "Digite o número do primeiro capítulo:"
        )
        saida = simpledialog.askfloat(
            "Capítulo final",
            f"Digite o número do último capítulo (total disponível: {total_caps}):",
        )

        if entrada is None or saida is None:
            messagebox.showwarning(
                "Aviso", "Você precisa informar o intervalo de capítulos."
            )
            return

        def baixar():
            capitulos = ml.buscar_capitulo_2(
                slug, capitulo_inicial=entrada, capitulo_final=saida
            )
            for capitulo in capitulos:
                cap_nome = capitulo["capitulo"]
                cap_path = caminho_base / f"Capitulo {cap_nome}"
                cap_path.mkdir(parents=True, exist_ok=True)

                response = requests.get(capitulo["url"])
                soup = BeautifulSoup(response.text, "html.parser")
                imagens = soup.find_all(ml.tag, class_=ml.class_name)

                self.progress["maximum"] = len(imagens)
                self.progress["value"] = 0

                def baixar_pagina(pagina):
                    url = pagina["src"]
                    nome_arquivo = cap_path / f"Pagina {imagens.index(pagina) + 1}.jpg"
                    salvar_imagem(url, nome_arquivo)
                    self.progress["value"] += 1
                    self.root.update_idletasks()
                    return nome_arquivo

                with ThreadPoolExecutor(max_workers=10) as executor:
                    arquivos = list(executor.map(baixar_pagina, imagens))

                try:
                    nome_pdf = f"Capitulo {cap_nome} - {slug}"
                    converter_para_pdf(cap_path, nome_pdf, arquivos)
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao converter para PDF: {e}")

            messagebox.showinfo("Concluído", "Download finalizado.")

        threading.Thread(target=baixar).start()

    def baixar_manga(self):
        sel = self.lista_resultados.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um mangá para baixar.")
            return

        index = sel[0]
        manga = self.mangas[index]
        id_manga = manga["id"]
        titulo = manga["titulo"]
        caminho_base = Path("downloads") / titulo
        caminho_base.mkdir(parents=True, exist_ok=True)

        capitulos_disponiveis = buscar_capitulos_por_id(id_manga)
        capitulos_numerados = [
            cap for cap in capitulos_disponiveis if cap.get("capitulo")
        ]
        total_caps = len(capitulos_numerados)

        entrada = simpledialog.askfloat(
            "Capítulo inicial", "Digite o número do primeiro capítulo:"
        )
        saida = simpledialog.askfloat(
            "Capítulo final",
            f"Digite o número do último capítulo (total disponível: {total_caps}):",
        )

        if entrada is None or saida is None:
            messagebox.showwarning(
                "Aviso", "Você precisa informar o intervalo de capítulos."
            )
            return

        def baixar():
            capitulos = []
            sem_numero_contador = 1
            capitulos_adicionados = set()

            for cap in buscar_capitulos_por_id(id_manga):
                cap_num = cap["capitulo"]
                if cap_num is None:
                    cap["capitulo"] = f"Sem número {sem_numero_contador}"
                    if cap["capitulo"] not in capitulos_adicionados:
                        sem_numero_contador += 1
                        capitulos.append(cap)
                        capitulos_adicionados.add(cap["capitulo"])
                else:
                    try:
                        cap_num_float = float(cap_num)
                        if entrada <= cap_num_float <= saida:
                            cap["capitulo"] = str(cap_num_float)
                            if cap["capitulo"] not in capitulos_adicionados:
                                capitulos.append(cap)
                                capitulos_adicionados.add(cap["capitulo"])
                    except ValueError:
                        print(f"Capítulo ignorado: {cap_num}")

            for capitulo in capitulos:
                capitulo_nome = str(capitulo["capitulo"])
                cap_path = caminho_base / f"Capitulo {capitulo_nome}"
                cap_path.mkdir(parents=True, exist_ok=True)

                paginas = buscar_paginas(capitulo["id"])

                self.progress["maximum"] = len(paginas)
                self.progress["value"] = 0

                def baixar_pagina_com_progresso(pagina):
                    nome_arquivo = cap_path / f"Pagina {pagina['pagina'] + 1}.jpg"
                    salvar_imagem(pagina["url"], nome_arquivo)
                    self.progress["value"] += 1
                    self.root.update_idletasks()
                    return nome_arquivo

                with ThreadPoolExecutor(max_workers=10) as executor:
                    arquivos = list(executor.map(baixar_pagina_com_progresso, paginas))

                try:
                    converter_para_pdf(
                        cap_path, f"Capítulo {capitulo_nome} - {cap['manga']}", arquivos
                    )
                    self.progress["value"] = 0
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao converter para PDF: {e}")

            messagebox.showinfo("Concluído", "Download finalizado.")

        threading.Thread(target=baixar).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = MangaApp(root)
    root.mainloop()
