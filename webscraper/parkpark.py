from datetime import datetime
import os
from urllib.parse import urljoin
import pandas as pd
import requests
from dotenv import load_dotenv

from utils import DateRange


## API Documentation: https://documenter.getpostman.com/view/10718386/2sB3QCUEaa


class ParkParkAPI:
    def __init__(self, api_key: str, date_range: DateRange):
        self.api_key = api_key
        self.date_range = date_range
        self.base_url = "https://spark.parkpark.dk/api/ignition/operator/report/"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": self.api_key,
        }

    def fetch_overview(self) -> pd.DataFrame:
        data = self._fetch_endpoint("overview")["data"]["parking_overview"]
        return pd.DataFrame(data)

    def fetch_creditnotes(self) -> pd.DataFrame:
        data = self._fetch_endpoint("creditnotes")["data"]["creditnotes"]
        return pd.DataFrame(data)

    def fetch_parkings(self) -> pd.DataFrame:
        data = self._fetch_endpoint("parkings")["data"]["parkings"]
        return pd.DataFrame(data)

    def _fetch_endpoint(self, endpoint: str):
        url = urljoin(self.base_url, endpoint)
        payload = {
            "start": self.date_range.start.strftime("%Y-%m-%d %H:%M:%S"),
            "end": self.date_range.end.strftime("%Y-%m-%d %H:%M:%S"),
        }
        response = requests.get(url, headers=self.headers, params=payload)
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("PARKPARK_API_KEY", "")

    start_date = datetime(2025, 10, 1)
    end_date = datetime(2025, 10, 2)
    date_range = DateRange(start_date, end_date)
    parkpark_api = ParkParkAPI(api_key, date_range)

    overview_data = parkpark_api.fetch_overview()
    print(overview_data)

    data = pd.DataFrame(overview_data)
    print(data.dtypes)
