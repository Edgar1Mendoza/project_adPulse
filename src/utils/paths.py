from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_data_dir(layer: str) -> Path:
    return get_project_root() / "data" / layer
