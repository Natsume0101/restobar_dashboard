"""
Extract text from PDF menu file
"""
import fitz  # PyMuPDF

pdf_path = 'Carta-La-Estacion-Restobar-QR-1.pdf'
text = ""

with fitz.open(pdf_path) as doc:
    for page in doc:
        text += page.get_text()

print(text)

# Save to text file for easy review
with open('menu_extracted.txt', 'w', encoding='utf-8') as f:
    f.write(text)

print("\n\n[Saved to menu_extracted.txt]")
