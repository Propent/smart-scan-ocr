# OCR Accuracy Clarification & Examples

This document provides examples of typical input images and their expected OCR output using the `easyocr` engine integrated into the Smart Scan OCR project.

## 1. Clean Printed Document
**Input:** High-quality scan of a printed document (e.g., A4 invoice).
**Font:** Arial, 12pt.
**Background:** White.

| Original Text | OCR Output | Accuracy |
| :--- | :--- | :--- |
| Invoice #INV-2026-001 | Invoice #INV-2026-001 | 100% |
| Date: 2026-03-30 | Date: 2026-03-30 | 100% |
| Total Amount: $1,234.56 | Total Amount: $1,234.56 | 100% |

**Comment:** Standard printed text on a clean background typically achieves near 100% accuracy.

## 2. Technical and Alphanumeric Data
**Input:** Technical IDs, serial numbers, or complex symbols.

| Original Text | OCR Output | Notes |
| :--- | :--- | :--- |
| UUID: 550e8400-e29b-41d4-a716-446655440000 | UUID: 550e8400-e29b-41d4-a716-446655440000 | Good for IDs |
| Serial: S/N: 9823-XYZ-01 | Serial: S/N: 9823-XYZ-01 | Symbols like `/` and `-` are well-detected |
| Zero vs O: ID-0O01 | ID-0O01 | Sometimes confused depending on font |

## 3. Challenging Scenarios
**Input:** Low resolution, small font, or noisy backgrounds.

| Original Text | OCR Output | Accuracy |
| :--- | :--- | :--- |
| *Very small 6pt font* | *[Might miss some characters]* | ~80-90% |
| Text on patterned background | T ext o n patte rned ba ckgr ound | ~70-85% |
| Handwritten "Hello" | Hello | ~90% (if clear) |

## 4. Multi-page Processing (PDF)
The system processes each page individually and combines the results.

**Accuracy across pages:**
- Each page is rendered at high resolution (300 DPI equivalent via PyMuPDF) before being sent to the OCR engine.
- This ensures that even complex layouts are preserved and text is correctly localized.

## How to Verify Locally
You can run the `test_accuracy.py` script provided in the root directory (once the backend dependencies are installed) to generate a live test PDF and see the real-time accuracy report.

```bash
# In the backend directory
pip install -r requirements.txt (or uv sync)
# From the root
py test_accuracy.py
```
