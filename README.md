# Extrator de Texto de PDF com DocTR

Este projeto utiliza a biblioteca DocTR para realizar o Reconhecimento Óptico de Caracteres (OCR) em arquivos PDF e extrair o texto bruto, incluindo suas geometrias. O script principal (`main.py`) processa um PDF, renderiza suas páginas como imagens e, em seguida, usa um modelo DocTR pré-treinado para detectar e reconhecer o texto. O resultado é salvo em um arquivo JSON.

## Funcionalidades

* Processa arquivos PDF de múltiplas páginas.
* Renderiza páginas PDF em imagens com DPI configurável (padrão: 400 DPI) usando PyMuPDF.
* Utiliza modelos OCR pré-treinados da biblioteca DocTR para detecção e reconhecimento de texto.
* Lida com a orientação de página e texto automaticamente (`assume_straight_pages=False`).
* Exporta a saída completa do DocTR (incluindo palavras, linhas, blocos, geometrias e confianças) para um arquivo JSON.
* Inclui um `JSONEncoder` personalizado para serializar corretamente arrays NumPy.
* Permite a configuração do nome do arquivo PDF de entrada através da variável de ambiente `PDF_FILE_NAME`.

## Pré-requisitos

* Python 3.8 ou superior.
* Poppler: Necessário para algumas funcionalidades do DocTR. O script tenta adicionar um caminho relativo (`layer/poppler/poppler-23.11.0/Library/bin`) ao PATH, mas a instalação adequada no sistema é recomendada.
    * **Linux:** `sudo apt-get install poppler-utils`
    * **macOS:** `brew install poppler`
    * **Windows:** Baixe o [binário do Poppler](https://github.com/oschwartz10612/poppler-windows/releases/), extraia e adicione o subdiretório `bin` ao PATH do sistema.

## Instalação

1.  Clone este repositório:
    ```bash
    git clone <url-do-seu-repositorio>
    cd <nome-do-seu-repositorio>
    ```

2.  Crie e ative um ambiente virtual (recomendado):
    ```bash
    python -m venv venv
    # No Windows
    venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```

3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
    Crie um arquivo `requirements.txt` com o seguinte conteúdo:
    ```txt
    python-doctr[tensorflow] # ou python-doctr[torch]
    PyMuPDF
    opencv-python
    numpy
    ```
    *(Escolha entre `tensorflow` ou `torch` como backend para o DocTR. O TensorFlow é geralmente mais fácil de configurar em diversas plataformas).*

## Uso

1.  Coloque o arquivo PDF que você deseja processar no diretório raiz do projeto.
2.  Defina a variável de ambiente `PDF_FILE_NAME` com o nome base do seu arquivo PDF (sem a extensão `.pdf`). Se não definida, o script pode usar um nome padrão ou você pode modificar o script para definir o nome do arquivo diretamente.
    * **Exemplo (Linux/macOS):**
        ```bash
        export PDF_FILE_NAME="meu_documento_enel"
        python main.py
        ```
    * **Exemplo (Windows PowerShell):**
        ```powershell
        $env:PDF_FILE_NAME = "meu_documento_enel"
        python main.py
        ```
    * Alternativamente, você pode modificar a linha no `main.py`:
        ```python
        # nome_base_arquivo = os.getenv('PDF_FILE_NAME')  # Padrão: 'documento'
        nome_base_arquivo = "56164154-959566847213" # Defina o nome base do seu PDF aqui
        ```

3.  Execute o script:
    ```bash
    python main.py
    ```

4.  O script irá gerar:
    * Mensagens no console indicando o progresso.
    * Um arquivo JSON (ex: `56164154-959566847213.json`) contendo os resultados brutos do OCR, incluindo o texto detectado, sua localização (geometria) e confiança.

## Estrutura do JSON de Saída

O arquivo JSON de saída contém uma estrutura detalhada fornecida pelo DocTR, que inclui:

* **pages**: Uma lista, onde cada item representa uma página do PDF.
    * **page_idx**: Índice da página.
    * **dimensions**: Altura e largura da página processada.
    * **orientation**: Orientação detectada da página.
    * **language**: Idioma detectado (se aplicável).
    * **blocks**: Lista de blocos de texto detectados na página.
        * **geometry**: Coordenadas da caixa delimitadora do bloco.
        * **lines**: Lista de linhas de texto dentro do bloco.
            * **geometry**: Coordenadas da caixa delimitadora da linha.
            * **words**: Lista de palavras dentro da linha.
                * **value**: O texto da palavra reconhecida.
                * **confidence**: A confiança do OCR para essa palavra.
                * **geometry**: Coordenadas da caixa delimitadora da palavra.

## Configuração

* **DPI para Renderização**: No arquivo `main.py`, a variável `dpi_para_ocr` (na seção `if __name__ == '__main__':`) e o parâmetro `dpi` na função `extrair_texto_pdf_para_json` estão configurados para `400`. Você pode ajustar este valor para balancear qualidade e velocidade de processamento. Valores mais altos podem melhorar a precisão para textos pequenos, mas aumentam o tempo de processamento.
* **Modelo DocTR**: O script usa `ocr_predictor(pretrained=True, assume_straight_pages=False)`. Para configurações avançadas de modelo, consulte a [documentação do DocTR](https://mindee.github.io/doctr/).

## Solução de Problemas

* **`TypeError: Object of type ndarray is not JSON serializable`**: Este erro é tratado pelo `NumpyEncoder` incluído no script.
* **Informações "Quebradas" ou Imprecisas**:
    * Tente aumentar o `dpi_para_ocr` (ex: para `600`).
    * Verifique a qualidade do PDF de entrada. PDFs escaneados de baixa qualidade podem gerar resultados piores.
    * Para PDFs "nascidos digitais" (texto embutido), a extração direta de texto com `PyMuPDF` (`page.get_text("text")`) pode ser mais rápida e precisa do que o OCR. O OCR é mais útil para PDFs baseados em imagem.
* **Erros de Dependência (TensorFlow/PyTorch)**: Certifique-se de que o backend escolhido (`tensorflow` ou `torch`) está corretamente instalado e compatível com sua versão do CUDA/cuDNN se estiver usando GPU.

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes (você precisará criar um arquivo `LICENSE` se desejar, por exemplo, com o [texto da licença MIT](https://opensource.org/licenses/MIT)).
