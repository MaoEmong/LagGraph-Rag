from __future__ import annotations

import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


def _import_pytesseract():
    try:
        import pytesseract  # type: ignore
    except Exception as exc:
        raise RuntimeError("pytesseract가 설치되어 있지 않습니다.") from exc
    return pytesseract


def _import_fitz():
    try:
        import fitz  # type: ignore
    except Exception as exc:
        raise RuntimeError("PyMuPDF(fitz)가 설치되어 있지 않습니다.") from exc
    return fitz


def _import_pil_image():
    try:
        from PIL import Image  # type: ignore
    except Exception as exc:
        raise RuntimeError("Pillow가 설치되어 있지 않습니다.") from exc
    return Image


def _ensure_tesseract_available(pytesseract_module) -> None:
    try:
        _ = pytesseract_module.get_tesseract_version()
    except Exception as exc:
        raise RuntimeError("Tesseract 실행 파일을 찾을 수 없습니다.") from exc


def ocr_pdf(path: Path, lang: str, dpi: int, max_pages: int) -> str:
    pytesseract = _import_pytesseract()
    fitz = _import_fitz()
    Image = _import_pil_image()
    _ensure_tesseract_available(pytesseract)

    max_pages = max(0, max_pages)
    texts: List[str] = []

    with fitz.open(path) as doc:
        page_count = doc.page_count
        page_limit = page_count if max_pages == 0 else min(page_count, max_pages)

        for page_index in range(page_limit):
            page = doc.load_page(page_index)
            matrix = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=matrix)
            if pix.alpha:
                pix = fitz.Pixmap(pix, 0)
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(image, lang=lang) or ""
            if text.strip():
                texts.append(text.strip())

    return "\n".join(texts)


def ocr_image(path: Path, lang: str) -> str:
    pytesseract = _import_pytesseract()
    Image = _import_pil_image()
    _ensure_tesseract_available(pytesseract)

    image = Image.open(path)
    text = pytesseract.image_to_string(image, lang=lang) or ""
    return text.strip()
