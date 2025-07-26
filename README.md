# EPUBMangaExtractor

# MangaLivre to EPUB Downloader 📚🖼️

Este projeto permite **baixar capítulos de mangás do site [MangaLivre](https://mangalivre.net)** e convertê-los automaticamente em arquivos **EPUB com imagens em alta qualidade**, utilizando **Selenium**, **BeautifulSoup** e **EbookLib**.

---

## 🚀 Funcionalidades

* Baixa imagens do capítulo atual e cria um arquivo `.epub`.
* Usa a **melhor qualidade de imagem disponível (srcset)**.
* Processa múltiplos capítulos de forma sequencial.
* Organiza as imagens, cria a capa, e gera o **TOC (Tabela de Conteúdo)**.
* Pula automaticamente capítulos com erro de carregamento de imagens, continuando para o próximo.
* Rodando em modo **headless** (sem abrir navegador).

---

## 🛠️ Dependências

* **Python 3.7+**
* **Google Chrome** e **ChromeDriver** compatíveis com sua versão do Chrome.

Para instalar as bibliotecas necessárias, basta usar o arquivo `requirements.txt`.

### 📦 Instalação

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/NonakaVal/EPUBMangaExtractor.git
   cd manga-livre-downloader
   ```

2. **Crie um ambiente virtual (opcional, mas recomendado):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Instale as dependências:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Instale o `ChromeDriver`:**

   Certifique-se de que o `chromedriver` está no seu **PATH**. Você pode baixá-lo [aqui](https://sites.google.com/a/chromium.org/chromedriver/).

   Após o download, verifique a instalação com:

   ```bash
   which chromedriver  # Linux/macOS
   where chromedriver  # Windows
   ```

---

## ▶️ Como usar

1. **Execute o script principal:**

   ```bash
   python main.py
   ```

2. **O script solicitará:**

   * **Caminho de saída**: Onde os arquivos EPUB serão salvos.
   * **Número de capítulos a baixar**.
   * **URL do primeiro capítulo**: Informe o link da página inicial do capítulo do mangá.

3. O script irá:

   * Baixar as imagens do capítulo.
   * Criar o EPUB com a estrutura e capa.
   * Ir automaticamente para o próximo capítulo.

---

## 📁 Estrutura do EPUB gerado

* **Capa**: A primeira imagem do capítulo será usada como capa.
* **Estilo**: Layout escuro com fundo preto e imagens centralizadas.
* **TOC (Tabela de Conteúdo)**: Cada página do mangá será uma entrada na tabela de conteúdo.
* **Fonte**: Link para a página original do capítulo.

---

## 🧪 Exemplo de uso

```bash
Digite o caminho de saída (pressione Enter para usar o padrão: /home/user/Documentos/Mangas):
Digite o número de capítulos a processar: 5
Digite o link do primeiro capítulo: https://mangalivre.net/capitulo/berserk/1
```

---

## ❗ Observações

* **Respeite os termos de uso** dos sites e os **direitos autorais** das obras.
* Este projeto é **para fins educacionais** e não deve ser utilizado para violar direitos autorais.
* O script foi desenvolvido para **mangás no site MangaLivre**, portanto pode não funcionar em outros sites sem ajustes.
* O layout do MangaLivre pode mudar com o tempo, e isso pode afetar o funcionamento do script.

---

## 📄 Estrutura do projeto

```
MangaLivre-to-EPUB/
│
├── main.py                # Script principal
├── requirements.txt       # Dependências do projeto
├── README.md              # Este arquivo
└── pages/                 # Pasta onde as imagens serão salvas temporariamente
```

---

## ✨ Futuras melhorias

* **Agrupamento por volume ou arco**: Adicionar suporte para gerar um EPUB por volume ou arco de história.
* **Interface de linha de comando** (CLI) com `argparse`: Tornar a execução mais flexível, sem necessidade de `input()`.
* **Interface gráfica** (GUI) com `Tkinter` ou `PyQt`: Facilitar o uso para usuários não técnicos.
* **Reprocessamento automático**: Reprocessar capítulos com erro ou falha de download de imagens.
* **Paralelismo com `asyncio`**: Implementar para melhorar a velocidade de download de imagens.

---

## 👨‍💻 Autor

**Val (Nonaka)**
Data Scientist | Pythonista | Fã de Mangás

---

## 🔗 Links úteis

* [MangaLivre](https://mangalivre.net)
* [EbookLib Documentation](https://ebooklib.readthedocs.io/)
* [Selenium Documentation](https://www.selenium.dev/documentation/)

---

### 💡 Sugestões de evolução:

* **Criar uma função de log** para registrar falhas de capítulos e permitir reprocessamento.
* **Automatizar o download de capítulos subsequentes** sem precisar de entrada do usuário.
* **Implementar controle de versão** no projeto para gerenciar atualizações ao longo do tempo.

---

Esse `README.md` pode ser modificado conforme o desenvolvimento do seu projeto ou novas funcionalidades. Se precisar de ajustes ou adição de novas seções, é só avisar!
