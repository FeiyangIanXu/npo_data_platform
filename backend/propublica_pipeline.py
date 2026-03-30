import argparse
from pathlib import Path

import pandas as pd

from db_utils import get_connection, get_db_path, resolve_table_name

FORM_TYPE_CODE_MAP = {
    "0": "990",
    "0.0": "990",
    "1": "990EO",
    "1.0": "990EO",
    "2": "990PF",
    "2.0": "990PF",
}


REQUIRED_COLUMNS = [
    "ein",
    "campus",
    "city",
    "st",
    "fiscal_year",
    "fiscal_month",
    "part_i_summary_12_total_revenue_cy",
    "employees",
]


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["ein"] = cleaned["ein"].astype(str).str.replace(".0", "", regex=False).str.zfill(9)

    if "propublica_form_type" in cleaned.columns:
        form_type = cleaned["propublica_form_type"].where(cleaned["propublica_form_type"].notna(), "")
        form_type = form_type.astype(str).str.strip()
        form_type = form_type.replace({"nan": "", "None": ""}).replace(FORM_TYPE_CODE_MAP)
        cleaned["propublica_form_type"] = form_type.astype("string")

    integer_columns = ["fiscal_year", "fiscal_month", "propublica_filing_count"]
    float_columns = [
        "part_i_summary_12_total_revenue_cy",
        "part_ix_statement_of_functional_expenses_25_total_functional_expenses_cy",
        "part_x_balance_sheet_16_total_assets_eoy",
        "part_x_balance_sheet_22_net_assets_or_fund_balances_eoy",
        "employees",
    ]

    for column in integer_columns:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce").astype("Int64")

    for column in float_columns:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    if "propublica_filing_date" in cleaned.columns:
        cleaned["propublica_filing_date"] = pd.to_datetime(cleaned["propublica_filing_date"], errors="coerce")

    return cleaned


def import_propublica_snapshot(csv_path: Path, dataset: str = "propublica") -> None:
    table_name = resolve_table_name(dataset)
    df = pd.read_csv(csv_path, dtype={"ein": str})

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Snapshot is missing required columns: {missing}")

    cleaned_df = normalize_dataframe(df)

    with get_connection() as conn:
        cleaned_df.to_sql(table_name, conn, if_exists="replace", index=False)
        cursor = conn.cursor()
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{table_name}_ein ON "{table_name}" (ein)')
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{table_name}_fiscal_year_month ON "{table_name}" (fiscal_year, fiscal_month)')
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{table_name}_state_city ON "{table_name}" (st, city)')
        conn.commit()

    print("=== ProPublica Backend Import Complete ===")
    print(f"CSV: {csv_path}")
    print(f"Database: {get_db_path()}")
    print(f"Imported table: {table_name}")
    print(f"Rows: {len(cleaned_df)}")
    print(f"Columns: {len(cleaned_df.columns)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Import ProPublica backend snapshot into SQLite as a parallel validation table.")
    parser.add_argument(
        "--csv",
        default=str(Path("data_harvester") / "output" / "propublica" / "propublica_backend_snapshot_20260319.csv"),
        help="Path to the ProPublica backend snapshot CSV.",
    )
    parser.add_argument(
        "--dataset",
        default="propublica",
        help="Target dataset key. Defaults to 'propublica'.",
    )
    args = parser.parse_args()

    import_propublica_snapshot(Path(args.csv), args.dataset)


if __name__ == "__main__":
    main()
