# Manga Downloader - Aplicativo com Interface Tkinter

## Descrição

Este é um aplicativo em Python com interface gráfica Tkinter para busca, visualização de informações e download de mangás utilizando duas fontes de dados: **MangaDex** e **MangaLivre**.

O sistema permite:

* Buscar mangás por nome em ambas as fontes.
* Visualizar informações detalhadas de cada mangá.
* Baixar capítulos completos.
* Converter imagens baixadas para PDF.
* Interface Dark Mode estilizada.

## Funcionalidades

* **Busca de mangás**: pesquisa pelo nome em MangaDex e MangaLivre.
* **Filtros de busca**: aplicação de filtros na consulta.
* **Visualização detalhada**: exibição de informações como título, autor, sinopse, capa, entre outros.
* **Download de capítulos**: com barra de progresso.
* **Conversão de imagens em PDF**.

## Tecnologias e Bibliotecas Utilizadas

* `tkinter` - Interface gráfica.
* `ttk` - Componentes estilizados.
* `PIL` (Pillow) - Manipulação de imagens.
* `requests` - Requisições HTTP.
* `BeautifulSoup` - Web scraping para MangaLivre.
* `tqdm` - Barra de progresso para downloads.
* `concurrent.futures` - Execução paralela de downloads.

## Estrutura de Arquivos

* `mangadex.py` - Funções para interagir com a API do MangaDex.
* `baixar_imagem.py` - Função para salvar imagens localmente.
* `converter_pdf.py` - Função para converter imagens para PDF.
* `get_cover.py` - Função para obter a capa do mangá.
* `sites.py` - Classe para manipular MangaLivre.
* `main.py` - Arquivo principal com a interface Tkinter (`MangaApp`).

## Como Executar

1. Clone o repositório:

```bash
git clone <seu-repositorio>
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Execute o script principal:

```bash
python main.py
```

## Dependências

* tkinter (embutido na maioria das instalações Python)
* pillow
* requests
* beautifulsoup4
* tqdm

Instale com:

```bash
pip install pillow requests beautifulsoup4 tqdm
```

## Uso

* Digite o nome do mangá na barra de pesquisa.
* Clique em **Buscar** (MangaDex) ou **Buscar \[ML]** (MangaLivre).
* Visualize as informações com **Info Manga**.
* Baixe atráves do **Baixar** dentro de **Info Manga**
  ou
* Baixe capítulos com **Baixar \[ML]**.

## Capturas de Tela

* Interface Dark Mode.
* Informações detalhadas do mangá.
* Visualização da capa.
* Barra de progresso.

## Créditos

* Desenvolvido por Luiz Souza.
* Baseado em APIs públicas e scraping para fins educacionais.

---

**Observação:** Use com responsabilidade e respeite os termos de uso dos sites consultados.
