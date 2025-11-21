import time
import os
from datetime import datetime
import pandas as pd


class RuntimeLogger:
    def __init__(
        self,
        path: str = "runtime_log.csv",
    ):
        self.path = path

    def save_log(
        self,
        start_time: datetime,
        status: str,
        file_path: str | None = None,
    ):
        self.start_time = start_time
        self.status = status
        self.log_df = pd.DataFrame(
            {"Start": [self.start_time], "Status": [self.status]}
        )
        if file_path is None:
            file_path = self.path
        # Check if file exists to determine if we should write header
        file_exists = os.path.exists(file_path)
        self.log_df.to_csv(file_path, index=False, mode="a", header=not file_exists)

    def get_last_runtime(self, status: str | None) -> datetime | None:
        try:
            df = pd.read_csv(self.path)
            if not df.empty:
                if status:
                    df.query(f"Status == '{status}'", inplace=True)  # Filter by status
                last_start_time: datetime = pd.to_datetime(df["Start"].iloc[-1])
                return datetime(
                    last_start_time.year, last_start_time.month, last_start_time.day
                )
            return None
        except FileNotFoundError:
            return None
