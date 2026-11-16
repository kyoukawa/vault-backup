import os
import pdfplumber

base_dir = r"C:\Users\chuan\Documents\知识库\试卷库"
out_dir = r"C:\Users\chuan\Documents\知识库\pdfplumber_out"

os.makedirs(out_dir, exist_ok=True)

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith('.pdf'):
            full_path = os.path.join(root, file)
            out_path = os.path.join(out_dir, os.path.basename(file))
            print(f"Processing: {full_path}")
            try:
                with pdfplumber.open(full_path) as pdf:
                    text = ''
                    for page in pdf.pages:
                        t = page.extract_text() or ''
                        text += t + '\n'
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(text)
                print(f"  -> saved to {out_path} ({len(text)} chars)")
            except Exception as e:
                print(f"  -> ERROR {file}: {e}")

print(f"Done. Output dir: {out_dir}")
