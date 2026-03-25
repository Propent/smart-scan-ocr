from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

def create_complex_pdf(path):
    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4
    
    # Page 1: Header and Intro
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(w/2, h - 100, "Complex Document Test")
    
    c.setFont("Helvetica", 12)
    text = [
        "This is a multi-page document designed to test the OCR engine.",
        "It contains different font sizes and layouts across multiple pages.",
        "The goal is to ensure that every page is processed and captured in the final output."
    ]
    y = h - 150
    for line in text:
        c.drawString(50, y, line)
        y -= 20
        
    c.showPage()
    
    # Page 2: Data Section
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, h - 50, "Section 2: System Specifications")
    
    c.setFont("Courier", 10)
    data = [
        "ID: 10293-AX",
        "STATUS: VERIFIED",
        "DATE: 2026-03-25",
        "LOCATION: SECTOR 7G",
        "AUTHOR: GEMINI-CLI"
    ]
    y = h - 80
    for line in data:
        c.drawString(70, y, "> " + line)
        y -= 25
        
    c.showPage()
    
    # Page 3: Footer/End
    c.setFont("Times-Italic", 14)
    c.drawCentredString(w/2, h/2, "End of Complex Document")
    c.drawCentredString(w/2, h/2 - 30, "Thank you for using the OCR Scan-to-PDF Engine.")
    
    c.save()

if __name__ == "__main__":
    os.makedirs('example/input', exist_ok=True)
    create_complex_pdf('example/input/complex_doc.pdf')
    print("Created example/input/complex_doc.pdf")
