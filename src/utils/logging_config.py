import logging

from src.utils.paths import get_project_root


def get_logger(name: str) -> logging.Logger:
    log_dir = get_project_root() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / "adpulse.log"),
        ],
    )

    return logging.getLogger(name)
