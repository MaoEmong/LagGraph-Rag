from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable

import docx
import pdfplumber

from ..config import settings
from .ocr import ocr_image, ocr_pdf

logger = logging.getLogger(__name__)

class ParseError(RuntimeError):
    pass


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_pdf(path: Path) -> str:
    chunks = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                if text:
                    chunks.append(text)
    except Exception as exc:
        raise ParseError(f"PDF 파싱 실패: {exc}")

    extracted = "\n".join(chunks)
    if settings.ocr_enabled and len(extracted.strip()) < settings.ocr_min_text_len:
        try:
            ocr_text = ocr_pdf(
                path,
                lang=settings.ocr_lang,
                dpi=settings.ocr_dpi,
                max_pages=settings.ocr_max_pages,
            )
            if ocr_text.strip():
                return ocr_text
        except Exception as exc:
            logger.warning("OCR 처리 실패: %s", exc)

    return extracted


def _read_docx(path: Path) -> str:
    try:
        doc = docx.Document(str(path))
        return "\n".join([p.text for p in doc.paragraphs if p.text])
    except Exception as exc:
        raise ParseError(f"DOCX 파싱 실패: {exc}")


def _read_image(path: Path) -> str:
    if not settings.ocr_enabled:
        raise ParseError("이미지 OCR이 비활성화되어 있습니다. OCR_ENABLED=true로 설정하세요.")

    try:
        return ocr_image(path, lang=settings.ocr_lang)
    except Exception as exc:
        raise ParseError(f"이미지 OCR 실패: {exc}")


def parse_file(path: Path) -> str:
    suffix = path.suffix.lower()

    if suffix == ".txt":
        return _read_text(path)
    if suffix == ".md":
        return _read_markdown(path)
    if suffix == ".pdf":
        return _read_pdf(path)
    if suffix == ".docx":
        return _read_docx(path)
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}:
        return _read_image(path)

    raise ParseError(f"지원하지 않는 확장자: {suffix}")
