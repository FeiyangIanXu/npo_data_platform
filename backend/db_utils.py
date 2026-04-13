import os
import sqlite3
from typing import Iterable, List, Optional


BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BACKEND_DIR, "irs.db")
DEFAULT_DATASET = "default"

DATASET_TABLES = {
    "default": "nonprofits",
    "propublica": "propublica_nonprofits",
}


def get_db_path() -> str:
    return DB_PATH


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def resolve_table_name(dataset: Optional[str] = None) -> str:
    dataset_key = (dataset or DEFAULT_DATASET).strip().lower()
    if dataset_key not in DATASET_TABLES:
        valid = ", ".join(sorted(DATASET_TABLES))
        raise ValueError(f"Unsupported dataset '{dataset}'. Valid datasets: {valid}")
    return DATASET_TABLES[dataset_key]


def get_supported_datasets() -> List[str]:
    return sorted(DATASET_TABLES)


def table_exists(table_name: str) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
            (table_name,),
        )
        return cursor.fetchone() is not None


def get_table_columns(table_name: str) -> List[str]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        return [row[1] for row in cursor.fetchall()]


def get_available_datasets() -> List[str]:
    available = []
    for dataset, table_name in DATASET_TABLES.items():
        if table_exists(table_name):
            available.append(dataset)
    return available


def ensure_columns(table_name: str, required_columns: Iterable[str]) -> None:
    existing_columns = set(get_table_columns(table_name))
    missing_columns = [column for column in required_columns if column not in existing_columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Table '{table_name}' is missing required columns: {missing}")
