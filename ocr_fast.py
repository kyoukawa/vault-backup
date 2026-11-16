import os
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import re

tesseract_cmd = r'C:\Users\chuan\tools\tesseract\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

def render_pdf_page(pdf_path, page_num, output_dir):
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    mat = fitz.Matrix(2, 2)  # 150 DPI - 快速模式
    pix = page.get_pixmap(matrix=mat)
    img_path = os.path.join(output_dir, f'page_{page_num+1}.png')
    pix.save(img_path)
    return img_path

def extract_text_with_ocr(image_path):
    custom_config = r'--oem 3 --psm 6 -l chi_sim+eng'
    text = pytesseract.image_to_string(Image.open(image_path), config=custom_config)
    return text.strip()

def process_pdf(pdf_path, output_dir):
    results = []
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        img_path = render_pdf_page(pdf_path, page_num, output_dir)
        text = extract_text_with_ocr(img_path)
        if text and len(text) > 50:  # 过滤空白页
            results.append({
                'page': page_num + 1,
                'text': text,
                'image_path': img_path
            })
    doc.close()
    return results

def generate_study_guide(all_results, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('# 解析几何题集学案\n\n')
        f.write('## 统计\n')
        f.write(f'总页数: {len(all_results)}\n')
        f.write(f'总问题数: {sum(len(r["text"].split(chr(10))) for r in all_results)}\n\n')
        for result in all_results:
            f.write(f'### 第{result["page"]}页\n\n')
            f.write(result['text'] + '\n\n')
            f.write('---\n\n')

if __name__ == "__main__":
    pdf_files = []
    for root, dirs, files in os.walk(r"C:\Users\chuan\Documents\知识库\试卷库"):
        for file in files:
            if file.endswith('.pdf'):
                path = os.path.join(root, file)
                if '数学' in file or any(math_name in path for math_name in ['数学', 'math']):
                    pdf_files.append(path)
    print(f"找到 {len(pdf_files)} 个数学PDF文件")
    
    all_results = []
    output_dir = r"C:\Users\chuan\Documents\知识库\ocr_results"
    os.makedirs(output_dir, exist_ok=True)
    
    for i, pdf_path in enumerate(pdf_files):
        print(f"处理 {i+1}/{len(pdf_files)}: {os.path.basename(pdf_path)}")
        results = process_pdf(pdf_path, output_dir)
        all_results.extend(results)
        print(f"  该文件找到 {len(results)} 页有文本")
    
    markdown_path = os.path.join(output_dir, "study_guide.md")
    generate_study_guide(all_results, markdown_path)
    print(f"学案生成完成: {markdown_path}")
