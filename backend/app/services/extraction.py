import fitz  # PyMuPDF
import os
from typing import Optional


def extract_text_from_pdf(file_path: str) -> dict:
    """
    Extract text from a PDF file page by page.
    
    Returns structured output containing:
    - full_text: all pages joined
    - pages: list of per-page content and metadata
    - metadata: document-level info
    - extraction_quality: assessment of how clean the text is
    """

    # Validate the file exists before attempting to open
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Open the PDF
    # fitz.open() handles corrupted files gracefully
    doc = fitz.open(file_path)

    pages = []
    total_chars = 0
    empty_pages = 0

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Extract text from this page
        # "text" mode returns plain text
        # "blocks" mode (used later) returns text with coordinates
        raw_text = page.get_text("text")

        # Clean the text
        cleaned_text = _clean_text(raw_text)

        # Count meaningful characters (not whitespace)
        char_count = len(cleaned_text.strip())
        total_chars += char_count

        # Flag pages with no extractable text
        is_empty = char_count < 10  # fewer than 10 chars = likely scanned
        if is_empty:
            empty_pages += 1

        pages.append({
            "page_number": page_num + 1,  # human-readable (1-indexed)
            "text": cleaned_text,
            "char_count": char_count,
            "is_empty": is_empty,
            "width": page.rect.width,
            "height": page.rect.height,
        })

    # Extract document-level metadata
    metadata = doc.metadata
    total_pages = len(doc)
    doc.close()

    # Assess overall extraction quality
    quality = _assess_quality(total_pages, empty_pages, total_chars)

    # Join all page text into one document string
    full_text = "\n\n".join(
        f"[Page {p['page_number']}]\n{p['text']}"
        for p in pages
        if not p["is_empty"]
    )

    return {
        "full_text": full_text,
        "pages": pages,
        "total_pages": total_pages,
        "empty_pages": empty_pages,
        "total_characters": total_chars,
        "metadata": {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
        },
        "extraction_quality": quality,
    }


def _clean_text(raw_text: str) -> str:
    """
    Clean extracted text.
    
    PDFs often have:
    - Excessive newlines from layout rendering
    - Hyphenated words split across lines (end-of-line hyphenation)
    - Ligature characters (fi, fl, ff rendered as single glyphs)
    """
    if not raw_text:
        return ""

    # Fix hyphenated line breaks: "computa-\ntion" → "computation"
    import re
    text = re.sub(r"-\n", "", raw_text)

    # Collapse multiple newlines into two (preserve paragraph breaks)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Replace ligature characters with their ASCII equivalents
    ligatures = {
        "\ufb00": "ff",
        "\ufb01": "fi",
        "\ufb02": "fl",
        "\ufb03": "ffi",
        "\ufb04": "ffl",
    }
    for ligature, replacement in ligatures.items():
        text = text.replace(ligature, replacement)

    return text.strip()


def _assess_quality(
    total_pages: int,
    empty_pages: int,
    total_chars: int
) -> str:
    """
    Return a human-readable quality assessment.
    
    This is useful for the frontend to warn users about
    low-quality extractions before they run expensive AI queries.
    """
    if total_pages == 0:
        return "failed"

    empty_ratio = empty_pages / total_pages

    if empty_ratio == 1.0:
        return "scanned_pdf_no_text"   # all pages empty → fully scanned
    elif empty_ratio > 0.5:
        return "poor"                   # majority scanned
    elif empty_ratio > 0.2:
        return "partial"                # some scanned pages
    elif total_chars < 100:
        return "minimal_text"           # very little content
    else:
        return "good"                   # clean digital PDF