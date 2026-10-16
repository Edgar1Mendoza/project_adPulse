from pathlib import Path

import pandas as pd


def check_idempotency(run_fn, output_path: Path) -> None:
    run_fn()
    first_run_df = pd.read_parquet(output_path)

    run_fn()
    second_run_df = pd.read_parquet(output_path)

    try:
        pd.testing.assert_frame_equal(first_run_df, second_run_df)
    except AssertionError as e:
        raise ValueError(f"Idempotency check failed: {e}") from e


def hash_rows(df: pd.DataFrame, key_columns: str, value_columns: list[str]) -> dict:
    row_hashes = pd.util.hash_pandas_object(df[value_columns], index=False)
    return dict(zip(df[key_columns], row_hashes))


def load_manifest(path: Path, key_column: str) -> dict:
    if not path.exists():
        return {}
    manifest_df = pd.read_parquet(path)
    return dict(zip(manifest_df[key_column], manifest_df["row_hash"]))


def save_manifest(hashes: dict, path: Path, key_column: str) -> None:
    manifest_df = pd.DataFrame(hashes.items(), columns=[key_column, "row_hash"])
    manifest_df.to_parquet(path, index=False)


def diff_rows(current_hashes: dict, previous_hashes: dict) -> dict:
    current_keys = set(current_hashes)
    previous_keys = set(previous_hashes)

    inserted = current_keys - previous_keys
    deleted = previous_keys - current_keys
    updated = {
        key
        for key in current_keys & previous_keys
        if current_hashes[key] != previous_hashes[key]
    }

    return {"inserted": inserted, "deleted": deleted, "updated": updated}
