from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


CSV_PATH = Path(__file__).with_name("Salary_Data.csv")
TABLE_NAME = "salary_data"
ENV_PATH = Path(__file__).with_name(".env")


def load_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url.strip()

    if ENV_PATH.exists():
        for raw_line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            if key.strip() == "DATABASE_URL":
                return value.strip().strip('"').strip("'")

    raise RuntimeError("DATABASE_URL was not found in the environment or .env file.")


def main() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

    try:
        original_df = pd.read_csv(CSV_PATH)
        original_rows = len(original_df)

        cleaned_df = original_df.dropna().copy()
        cleaned_rows = len(cleaned_df)
        dropped_rows = original_rows - cleaned_rows

        database_url = load_database_url()
        engine = create_engine(database_url)

        with engine.begin() as connection:
            cleaned_df.head(0).to_sql(
                TABLE_NAME,
                con=connection,
                if_exists="replace",
                index=False,
            )

            inserted_rows = 0
            if not cleaned_df.empty:
                cleaned_df.to_sql(
                    TABLE_NAME,
                    con=connection,
                    if_exists="append",
                    index=False,
                    method="multi",
                    chunksize=1000,
                )
                inserted_rows = cleaned_rows

        print("Load completed successfully.")
        print(f"Source rows: {original_rows}")
        print(f"Rows after cleaning: {cleaned_rows}")
        print(f"Rows dropped: {dropped_rows}")
        print(f"Rows inserted into {TABLE_NAME}: {inserted_rows}")

    except Exception as exc:
        print(f"Failed to load salary data: {exc}")
        raise


if __name__ == "__main__":
    main()