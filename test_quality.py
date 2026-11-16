import subprocess, sys

# 1. 检查tesseract语言
r = subprocess.run(['tesseract', '--list-langs'], capture_output=True, text=True)
print('TESS_LANG:', r.stdout, r.stderr)

# 2. pdfplumber文本提取
try:
    import pdfplumber
    pdf_path = r"C:\Users\chuan\Documents\知识库\试卷库\2024\一模\数学\2024北京东城高三一模数学.pdf"
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text() or ''
    with open(r'C:\Users\chuan\Documents\知识库\test_pdfplumber.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    print('PDFPLUMBER_OK len=', len(text))
except Exception as e:
    print('PDFPLUMBER_FAIL:', repr(e))

# 3. PyMuPDF渲染 + pytesseract OCR
try:
    import fitz
    from PIL import Image
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\chuan\tools\tesseract\tesseract.exe'
    pdf_path = r"C:\Users\chuan\Documents\知识库\试卷库\2024\一模\数学\2024北京东城高三一模数学.pdf"
    doc = fitz.open(pdf_path)
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
    img_path = r'C:\Users\chuan\Documents\知识库\test_page1.png'
    pix.save(img_path)
    doc.close()
    try:
        ocr_text = pytesseract.image_to_string(Image.open(img_path), lang='chi_sim+eng')
    except Exception as e2:
        print('OCR chi_sim fail:', repr(e2))
        ocr_text = pytesseract.image_to_string(Image.open(img_path), lang='eng')
    with open(r'C:\Users\chuan\Documents\知识库\test_ocr.txt', 'w', encoding='utf-8') as f:
        f.write(ocr_text)
    print('OCR_OK len=', len(ocr_text))
except Exception as e:
    print('OCR_FAIL:', repr(e))
