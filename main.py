import json
import os
import fitz  # PyMuPDF (para manipulação de PDF e rasterização)
import cv2   # OpenCV (usado aqui para conversão de espaço de cores, se necessário)
import numpy as np
from doctr.models import ocr_predictor

# Boa prática: Configurar o PATH para dependências externas como Poppler.
script_base_dir = os.path.dirname(os.path.abspath(__file__))
poppler_path_relative = os.path.join('layer', 'poppler', 'poppler-23.11.0', 'Library', 'bin')
poppler_full_path = os.path.join(script_base_dir, poppler_path_relative)

# Adiciona o Poppler ao PATH apenas se o diretório existir e não estiver já no PATH
if os.path.exists(poppler_full_path) and poppler_full_path not in os.environ['PATH']:
    os.environ['PATH'] += os.pathsep + poppler_full_path
    print(f"Adicionado ao PATH: {poppler_full_path}")


# Classe JSONEncoder personalizada para lidar com tipos NumPy
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()  # Converte arrays NumPy para listas Python
        if isinstance(obj, (np.generic, np.bool_)): # Lida com escalares NumPy (float, int, bool)
            return obj.item()    # Converte para o tipo Python nativo equivalente
        return json.JSONEncoder.default(self, obj)


def prepare_image_for_ocr(image_np_rgb):
    """
    Prepara a imagem RGB (NumPy array) para o OCR.
    Atualmente, esta função garante que se está trabalhando com uma cópia da imagem.
    """
    return image_np_rgb.copy()

def extrair_texto_pdf_para_json(caminho_pdf, caminho_json_saida, dpi=400): # DPI alterado para 400
    """
    Extrai todo o texto detectado de um arquivo PDF usando doctr e salva o resultado
    bruto (incluindo geometrias) em um arquivo JSON.

    Args:
        caminho_pdf (str): O caminho para o arquivo PDF de entrada.
        caminho_json_saida (str): O caminho para salvar o arquivo JSON de saída.
        dpi (int): A resolução (dots per inch) para renderizar as páginas do PDF.
    """
    try:
        print("Carregando o modelo OCR (doctr)...")
        model = ocr_predictor(pretrained=True, assume_straight_pages=False)

        print(f"Processando arquivo PDF: {caminho_pdf}")
        if not os.path.exists(caminho_pdf):
            print(f"Erro: Arquivo PDF não encontrado em '{caminho_pdf}'")
            return

        pdf_document = fitz.open(caminho_pdf)
        num_pages = len(pdf_document)
        print(f"O PDF contém {num_pages} página(s). Renderizando cada página a {dpi} DPI.")

        imagens_para_ocr = []
        for page_num in range(num_pages):
            print(f"  - Renderizando página {page_num + 1}/{num_pages}...")
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False)

            if pix.alpha:
                img_np_raw = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, 4)
                img_np_rgb = cv2.cvtColor(img_np_raw, cv2.COLOR_RGBA2RGB)
            else:
                img_np_rgb = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, 3)

            img_pronta_para_ocr = prepare_image_for_ocr(img_np_rgb)
            imagens_para_ocr.append(img_pronta_para_ocr)

        pdf_document.close()

        if not imagens_para_ocr:
            print("Nenhuma página foi convertida para imagem. Abortando o processo de OCR.")
            return

        print("Iniciando o reconhecimento de texto (OCR) com doctr...")
        result = model(imagens_para_ocr)

        print(f"Exportando os resultados brutos do OCR para o arquivo JSON: {caminho_json_saida}")
        json_output_doctr = result.export()

        with open(caminho_json_saida, 'w', encoding='utf-8') as f:
            json.dump(json_output_doctr, f, ensure_ascii=False, indent=4, cls=NumpyEncoder)

        print(f"Resultados brutos do OCR salvos com sucesso em '{caminho_json_saida}'.")

    except Exception as e:
        print(f"Ocorreu um erro crítico durante o processo: {e}")
        import traceback
        traceback.print_exc()
        print("\nSugestões para solução de problemas:")
        print("  - Verifique se todas as dependências necessárias estão instaladas corretamente:")
        print("    pip install python-doctr[tensorflow]  (ou python-doctr[torch])")
        print("    pip install PyMuPDF opencv-python numpy")
        print("  - Confirme se o caminho para o arquivo PDF de entrada está correto e se o arquivo é válido.")
        print("  - Verifique a configuração do Poppler PATH, se aplicável.")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Obter o nome base do arquivo da variável de ambiente ou usar um padrão
    nome_base_arquivo = os.getenv('PDF_FILE_NAME')  # Padrão: 'documento'

    # Construir os nomes dos arquivos de entrada e saída
    nome_arquivo_pdf_entrada = f"{nome_base_arquivo}.pdf"
    caminho_pdf_entrada = os.path.join(script_dir, nome_arquivo_pdf_entrada)

    nome_arquivo_json_saida = f"{nome_base_arquivo}.json"
    caminho_json_saida = os.path.join(script_dir, nome_arquivo_json_saida)

    dpi_para_ocr = 400 # DPI alterado para 400

    extrair_texto_pdf_para_json(caminho_pdf_entrada, caminho_json_saida, dpi=dpi_para_ocr)
