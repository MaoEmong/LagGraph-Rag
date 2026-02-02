from __future__ import annotations

from pathlib import Path
from typing import Iterable, List


SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".pdf",
    ".docx",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
}


def discover_files(path: str, recursive: bool = True) -> List[Path]:
    base = Path(path)
    if base.is_file():
        return [base]

    if not base.is_dir():
        return []

    pattern = "**/*" if recursive else "*"
    files = [p for p in base.glob(pattern) if p.is_file()]
    return [p for p in files if p.suffix.lower() in SUPPORTED_EXTENSIONS and not p.name.startswith(".")]
