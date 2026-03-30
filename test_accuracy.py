import sys
import os
import io
from difflib import SequenceMatcher

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def create_test_pdf(path, tests):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4
    
    y = h - 50
    for test_name, text in tests.items():
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, f"Test: {test_name}")
        y -= 30
        
        c.setFont("Helvetica", 12)
        lines = text.split('\n')
        for line in lines:
            c.drawString(70, y, line)
            y -= 20
        y -= 20
        
    c.save()

def calculate_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def check_accuracy():
    test_cases = {
        "Simple Text": "The quick brown fox jumps over the lazy dog.",
        "Numbers and Symbols": "Account #12345-6789 | Total: $1,234.56",
        "Dates and Addresses": "Date: 2026-03-30\n123 OCR Lane, Scan City, 90210",
        "Technical ID": "UUID: 550e8400-e29b-41d4-a716-446655440000"
    }
    
    os.makedirs('example/input', exist_ok=True)
    pdf_path = 'example/input/accuracy_test.pdf'
    
    try:
        create_test_pdf(pdf_path, test_cases)
    except ImportError:
        print("Error: reportlab not installed. Cannot generate test PDF.")
        return

    print(f"--- OCR Precision & Accuracy Report ---")
    print(f"Input file: {pdf_path}\n")
    
    try:
        from app.services.ocr_service import ocr_service
    except (ImportError, ModuleNotFoundError):
        print("Note: OCR Service not available (missing dependencies).")
        return

    with open(pdf_path, 'rb') as f:
        file_bytes = f.read()
    
    results = ocr_service.extract_text(file_bytes)
    
    # Combined text for checking multi-block lines
    full_detected_text = " ".join([r['text'] for r in results])
    
    print(f"{'EXPECTED LINE':<45} | {'ACCURACY %':<12} | {'MATCH'}")
    print("-" * 80)
    
    total_score = 0
    total_lines = 0
    
    for name, expected in test_cases.items():
        expected_lines = expected.split('\n')
        for line in expected_lines:
            # Find the best matching block or use combined text for comparison
            # We compare the expected line against the whole detected text to handle splits
            # but we use a window-based approach or just simple ratio for the report
            
            # Simple approach: Find the best similarity ratio for this line in the detected text
            max_sim = 0
            # Check individual blocks
            for res in results:
                sim = calculate_similarity(line.lower(), res['text'].lower())
                if sim > max_sim:
                    max_sim = sim
            
            # Also check if it's split across blocks (fuzzy check)
            combined_sim = calculate_similarity("".join(line.lower().split()), "".join(full_detected_text.lower().split()))
            # If combined is very high, use a boosted score
            if "".join(line.lower().split()) in "".join(full_detected_text.lower().split()):
                max_sim = max(max_sim, 1.0)
            else:
                max_sim = max(max_sim, combined_sim * 0.9) # Slight penalty for being split

            accuracy_pct = max_sim * 100
            status = "✅ PASS" if accuracy_pct > 90 else "❌ FAIL"
            
            print(f"{line[:43]:<45} | {accuracy_pct:>10.2f}% | {status}")
            
            total_score += accuracy_pct
            total_lines += 1

    overall_accuracy = total_score / total_lines if total_lines > 0 else 0
    print("-" * 80)
    print(f"{'OVERALL DOCUMENT ACCURACY':<45} | {overall_accuracy:>10.2f}%")
    print("-" * 80)

if __name__ == "__main__":
    check_accuracy()
