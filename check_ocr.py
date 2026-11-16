import sys
mods = ["PIL", "pytesseract", "fitz", "pdfplumber", "PyPDF2"]
for m in mods:
    try:
        __import__(m)
        print("OK:", m)
    except ImportError as e:
        print("MISSING:", m, str(e))
