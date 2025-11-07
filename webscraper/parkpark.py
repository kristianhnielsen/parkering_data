from datetime import datetime
import os
from urllib.parse import urljoin
import pandas as pd
import requests
from dotenv import load_dotenv


class ParkParkAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://spark.parkpark.dk/api/ignition/operator/report/"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": self.api_key,
        }

    def fetch_overview(self, start: datetime, end: datetime):
        return self.fetch_endpoint("overview", start, end)

    def fetch_creditnotes(self, start: datetime, end: datetime):
        return self.fetch_endpoint("creditnotes", start, end)

    def fetch_parkings(self, start: datetime, end: datetime):
        return self.fetch_endpoint("parkings", start, end)

    def fetch_endpoint(self, endpoint: str, start: datetime, end: datetime):
        url = urljoin(self.base_url, endpoint)
        payload = {
            "start": start.strftime("%Y-%m-%d %H:%M:%S"),
            "end": end.strftime("%Y-%m-%d %H:%M:%S"),
        }
        response = requests.get(url, headers=self.headers, params=payload)
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("PARKPARK_API_KEY", "")
    parkpark_api = ParkParkAPI(api_key)

    start_date = datetime(2025, 10, 1)
    end_date = datetime(2025, 10, 2)

    overview_data = parkpark_api.fetch_overview(start_date, end_date)
