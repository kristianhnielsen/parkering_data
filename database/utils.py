import pandas as pd
from sqlalchemy import inspect
import database.operations as db_ops


def safe_na_datetime(item: pd.Series):
    """SQLAlchemy cannot process pd.NaT as None.
    Returns None when the value is pd.NaT (or pd.Na)"""
    return item.apply(lambda value: None if pd.isna(value) else value)


def export_all_tables_to_excel(output_path: str = "export.xlsx"):
    engine = db_ops.engine
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    # Excel sheet names must be <= 31 chars; we truncate and ensure uniqueness
    seen = {}

    def unique_sheet_name(name):
        sheet = name[:31]
        count = seen.get(sheet, 0)
        seen[sheet] = count + 1
        return (
            f"{sheet}"
            if count == 0
            else f"{sheet[:max(0, 31 - len(str(count)))]}_{count}"
        )

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for table in table_names:
            df = pd.read_sql_table(table, con=engine)
            sheet_name = unique_sheet_name(table)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            df.to_csv(f"{table}.csv", index=False)
    print(f"Exported {len(table_names)} tables to {output_path}")
