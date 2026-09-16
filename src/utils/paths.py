import os
from pathlib import Path

from dotenv import load_dotenv


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_data_dir(layer: str) -> Path:
    return get_project_root() / "data" / layer


def get_source_dir() -> Path:
    load_dotenv()
    return Path(os.environ["DOWNLOADS_SOURCE_DIR"])
