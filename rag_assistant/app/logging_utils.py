import logging
from pathlib import Path

from .config import settings


def setup_logging() -> None:
    # 로그 디렉토리 준비
    Path(settings.log_path).mkdir(parents=True, exist_ok=True)

    log_file = Path(settings.log_path) / "app.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
