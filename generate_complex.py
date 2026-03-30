from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import os

def create_complex_pdf(path):
    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4
    
    # Page 1: Mixed Fonts and Small Text
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(w/2, h - 50, "Advanced OCR Stress Test")
    
    c.setFont("Times-Roman", 12)
    c.drawString(50, h - 100, "This section tests Serif font recognition and small text handling.")
    
    c.setFont("Times-Roman", 8)
    c.drawString(50, h - 120, "SMALL TEXT TEST: This is 8pt Times Roman font. It should be legible to high-res OCR.")
    
    # Page 2: Table Simulation (Fixed-width data)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, h - 50, "Section 2: Tabular Data Extraction")
    
    c.setFont("Courier", 10)
    headers = ["ID", "DESCRIPTION", "QTY", "PRICE", "TOTAL"]
    data = [
        ["101", "Micro-Processor XT", "5", "$120.00", "$600.00"],
        ["102", "Logic Board v2.1", "2", "$450.00", "$900.00"],
        ["103", "Thermal Paste", "10", "$15.50", "$155.00"]
    ]
    
    y = h - 80
    x_offsets = [50, 100, 250, 320, 400]
    
    # Draw Headers
    for i, header in enumerate(headers):
        c.drawString(x_offsets[i], y, header)
    
    y -= 5
    c.line(50, y, 480, y)
    y -= 15
    
    # Draw Rows
    for row in data:
        for i, val in enumerate(row):
            c.drawString(x_offsets[i], y, val)
        y -= 20

    # Page 3: Rotated and Skewed Text (Challenging)
    c.showPage()
    c.saveState()
    c.setFont("Helvetica-Bold", 16)
    c.translate(w/2, h/2)
    c.rotate(15) # Rotate 15 degrees
    c.drawCentredString(0, 0, "ROTATED TEXT TEST (15 DEG)")
    c.restoreState()
    
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(w/2, 50, "Confidential - Smart Scan OCR Internal Test")
    
    c.save()

if __name__ == "__main__":
    os.makedirs('example/input', exist_ok=True)
    create_complex_pdf('example/input/complex_doc.pdf')
    print("Created example/input/complex_doc.pdf")
