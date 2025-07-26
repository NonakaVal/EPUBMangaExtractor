import os
import requests
from bs4 import BeautifulSoup
from ebooklib import epub
from PIL import Image
from io import BytesIO
import re
import time
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MangaLivreToEPUB:
    def __init__(self, chapter_url, output_filename, title, author, output_dir, driver):
        self.chapter_url = chapter_url
        self.output_filename = output_filename
        self.title = title
        self.author = author
        self.output_dir = output_dir
        self.pages_dir = os.path.join(output_dir, "pages")
        self.image_urls = []
        self.driver = driver
        os.makedirs(self.pages_dir, exist_ok=True)

    def sanitize_filename(self, name):
        """Sanitiza o nome do arquivo, removendo caracteres especiais e espaços."""
        name = re.sub(r"[\\/:*?\"<>|]", "", name)  # Remove caracteres especiais
        name = re.sub(r"\s+", "_", name.strip())  # Substitui espaços por "_"
        name = re.sub(r"_+", "_", name)  # Remove múltiplos underscores
        return name[:100]  # Limita o comprimento do nome a 100 caracteres

    def format_filename(self, chapter_number):
        """Formata o nome do arquivo de forma limpa e padronizada."""
        formatted_title = self.sanitize_filename(self.title.lower())
        # Remove sufixos como "_pt-br", "_manga_livre", etc.
        formatted_title = re.sub(r'(_|-)?manga[_\-]?livre.*$', '', formatted_title, flags=re.IGNORECASE)
        formatted_title = re.sub(r'(_|-)?pt[_\-]?br$', '', formatted_title, flags=re.IGNORECASE)
        formatted_title = formatted_title.strip('_-')  # Limpa underscores finais
        return f"{formatted_title}.epub"



    def fetch_image_urls(self):
        """Busca as URLs das imagens do capítulo."""
        try:
            self.driver.get(self.chapter_url)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.chapter-image-container img"))
            )

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            self.image_urls = self._extract_image_urls(soup)

            if not self.image_urls:
                print("[AVISO] Nenhuma imagem encontrada.")
                return False

            print(f"[INFO] Encontradas {len(self.image_urls)} imagens no capítulo.")
            return True
        except Exception as e:
            print(f"[ERRO] Falha ao buscar imagens: {e}")
            return False

    def _extract_image_urls(self, soup):
        """Extrai URLs de imagem da página HTML."""
        image_urls = []
        for img in soup.select('div.chapter-image-container img'):
            srcset = img.get('srcset') or img.get('data-srcset')  # [MODIFICADO] garante maior qualidade
            if srcset:
                highest_res_url = self._get_highest_resolution_url(srcset)
                image_urls.append(highest_res_url)
            else:
                img_url = img.get('src') or img.get('data-src')
                if img_url:
                    image_urls.append(img_url)
        return image_urls


    def _get_highest_resolution_url(self, srcset):
        """Obtém a URL de maior resolução a partir do atributo srcset."""
        srcset_urls = [s.strip().split() for s in srcset.split(',')]
        return sorted(srcset_urls, key=lambda x: int(x[1].replace('w', '')), reverse=True)[0][0]

    def download_image(self, url, filename):
        """Baixa e salva a imagem no diretório de páginas."""
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': self.chapter_url})
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            img_format = 'PNG' if img.mode in ('RGBA', 'LA') else 'JPEG'
            img_path = os.path.join(self.pages_dir, filename)
            img.save(img_path, format=img_format, optimize=True)
            return img_path
        except Exception as e:
            print(f"[ERRO] Falha ao baixar {url}: {e}")
            return None

    def download_all_pages(self):
        """Baixa todas as páginas do capítulo."""
        success = self.fetch_image_urls()
        if not success:
            return []

        return [self.download_image(url, f"page_{i + 1:03d}.png") for i, url in enumerate(tqdm(self.image_urls, desc="Baixando Imagens", unit="imagem"))]

    def create_epub(self, image_paths):
        """Cria o arquivo EPUB com as imagens do capítulo."""
        if not image_paths:
            print("[ERRO] Nenhuma imagem para criar EPUB")
            return False

        book = epub.EpubBook()
        book.set_identifier(f"manga_{int(time.time())}")
        book.set_title(self.title)
        book.set_language("pt")
        book.add_author(self.author)

        self._add_styles(book)
        self._create_intro_page(book)

        spine = ['nav']
        toc = []
        self._add_images_to_epub(book, image_paths, spine, toc)

        # Adiciona uma linha em branco e depois a entrada "Fonte: link"
        toc.append(epub.Link('#', '', ''))  # Cria um item de "espaço em branco" (sem link)
        toc.append(epub.Link(self.chapter_url, f"Fonte: {self.chapter_url}", "source_link"))

        book.toc = tuple(toc)
        book.spine = spine
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        epub.write_epub(self.output_filename, book, {})
        print(f"[SUCESSO] EPUB gerado: {self.output_filename}")
        return True


    def _add_styles(self, book):
        """Adiciona o estilo CSS ao EPUB."""
        style = '''
        * { margin: 0; padding: 0; }
        html, body {
            width: 100%;
            height: 100%;
            background-color: black;
        }
        img {
            width: 100%;
            height: 100%;
            object-fit: contain;
            display: block;
            image-rendering: auto;
        }
        '''
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
        book.add_item(nav_css)

    def _create_intro_page(self, book):
        """Cria uma página inicial com o título e link da fonte."""
        intro = epub.EpubHtml(title="Início", file_name="intro.xhtml", lang="pt")
        intro.content = f'''
        <html xmlns="http://www.w3.org/1999/xhtml">
            <head>
                <title>{self.title}</title>
                <link rel="stylesheet" type="text/css" href="style/nav.css"/>
            </head>
            <body style="color:white; background-color:black; text-align:center; padding: 50px;">
                <h1>{self.title}</h1>
                <p>Fonte original: <a href="{self.chapter_url}" style="color:lightblue;">Clique aqui para acessar o capítulo original</a></p>
            </body>
        </html>
        '''
        book.add_item(intro)

    def _add_images_to_epub(self, book, image_paths, spine, toc):
        """Adiciona as imagens do capítulo ao EPUB."""
        for i, image_path in enumerate(image_paths):
            img_filename = os.path.basename(image_path)
            with open(image_path, 'rb') as f:
                img_item = epub.EpubItem(
                    uid=f"img_{i}",
                    file_name=f"images/{img_filename}",
                    media_type="image/png",
                    content=f.read()
                )
                book.add_item(img_item)

            chapter = epub.EpubHtml(
                title=f"Página {i+1}",
                file_name=f"page_{i+1:03d}.xhtml",
                lang="pt"
            )
            chapter.content = f'''
            <html xmlns="http://www.w3.org/1999/xhtml">
                <head>
                    <title>Página {i+1}</title>
                    <link rel="stylesheet" type="text/css" href="style/nav.css"/>
                </head>
                <body>
                    <img src="images/{img_filename}" alt="Página {i+1}"/>
                </body>
            </html>
            '''
            book.add_item(chapter)
            spine.append(chapter)
            toc.append(epub.Link(chapter.file_name, f"Página {i+1}", f"page_{i+1:03d}"))

            if i == 0:  # Define a capa como a primeira imagem
                with open(image_path, 'rb') as cover_file:
                    book.set_cover("cover.png", cover_file.read())

    def run(self):
        """Baixa as imagens e cria o EPUB."""
        image_paths = self.download_all_pages()
        if image_paths:
            return self.create_epub(image_paths)
        return False

def get_next_chapter(driver):
    """Busca o próximo capítulo."""
    try:
        next_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.next-chapter-btn"))
        )
        next_url = next_btn.get_attribute('href')
        if next_url and next_url != driver.current_url:
            print(f"[INFO] Próximo capítulo encontrado: {next_url}")
            return next_url
    except:
        print("[AVISO] Botão próximo não encontrado, tentando método alternativo...")
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            next_link = soup.find('a', class_='next-chapter-btn') or \
                       soup.find('a', string=re.compile(r'próximo|next', re.IGNORECASE))
            
            if next_link and next_link.get('href'):
                next_url = next_link['href']
                if next_url != driver.current_url:
                    print(f"[INFO] Próximo capítulo encontrado via HTML: {next_url}")
                    return next_url
        except Exception as e:
            print(f"[ERRO] Método alternativo também falhou: {e}")
    
    print("[AVISO] Não foi possível encontrar o link para o próximo capítulo")
    return None

def setup_driver():
    """Configura o WebDriver para o Selenium."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    driver = webdriver.Chrome(options=options)
    return driver

def main():
    """Função principal que roda o processo de baixar e criar o EPUB."""

    # [MODIFICADO] Caminho de saída agora como input com valor padrão
    default_dir = "/home/nonaka/Documentos/Mangas/berserk/"
    user_input = input(f"Digite o caminho de saída (pressione Enter para usar o padrão: {default_dir}): ").strip()
    output_dir = user_input if user_input else default_dir
    os.makedirs(output_dir, exist_ok=True)

    num_chapters = 500 # int(input("Digite o número de capítulos a processar: "))
    driver = setup_driver()
    start_url = input("Digite o link do primeiro capítulo: ")
    current_url = start_url

    for chapter_num in range(1, num_chapters + 1):
        try:
            print(f"\n=== PROCESSANDO CAPÍTULO {chapter_num} ===")

            driver.get(current_url)
            title = driver.title.split('|')[0].strip() if '|' in driver.title else driver.title.strip()
            safe_title = title
            output_filename = os.path.join(output_dir, MangaLivreToEPUB('', '', safe_title, '', '', driver).format_filename(chapter_num))

            manga = MangaLivreToEPUB(
                chapter_url=current_url,
                output_filename=output_filename,
                title=f"{safe_title} - Capítulo {chapter_num}",
                author="Kentaro Miura",
                output_dir=output_dir,
                driver=driver
            )

            success = manga.run()
            if not success:
                print(f"[AVISO] Falha ao processar capítulo {chapter_num}, pulando para o próximo...\n")
                current_url = get_next_chapter(driver)
                if not current_url:
                    print("[AVISO] Não há mais capítulos disponíveis, encerrando...")
                    break
                continue  # [NOVO] pula para o próximo laço


            current_url = get_next_chapter(driver)
            if not current_url:
                print("[AVISO] Não há mais capítulos disponíveis, interrompendo...")
                break

            time.sleep(2)

        except Exception as e:
            print(f"[ERRO CRÍTICO] Falha ao processar capítulo {chapter_num}: {e}")
            break

    driver.quit()
    print("\nProcesso concluído!")


if __name__ == "__main__":
    main()
