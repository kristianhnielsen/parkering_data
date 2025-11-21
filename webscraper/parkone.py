from datetime import datetime, timezone
import pandas as pd
import requests
from dotenv import load_dotenv
import os
from urllib.parse import urljoin

from webscraper.utils import DateRange


class ParkOneAPI:
    def __init__(self, date_range: DateRange):
        load_dotenv()
        self.date_range = date_range
        self._auth_token = os.getenv("PARKONE_API_KEY", "")
        self.headers = {
            "content-type": "application/json",
            "authorization": self._auth_token,
        }
        self.base_url = "https://api.parkone.dk/v1/"
        self.municipality = "vejle"

    def get_all_parkings(self):
        """
        Retrieves all the active parkings for all municipalities.

        Response:
        parkingStartTime: string 				(Parking Start At)
        parkingStopAt: string 				(Estimated Parking Stop At)
        vehicleRegId: string 					(Licence Plate Number)
        municipality: string 					(Operator)
        zone: string 						(Zone Name)
        """
        endpoint = "Parkings/getAllParkings"
        url = urljoin(base=self.base_url, url=endpoint)
        df = pd.DataFrame()

        # API docs specify no date ranges > 6 months. We split into 30 day intervals to be safe.
        date_ranges = self.date_range.split(interval_days=30)
        for date_range in date_ranges:
            try:
                params = {
                    "municipality": self.municipality,
                    "startDate": self._dt_ms_format(date_range.start),
                    "endDate": self._dt_ms_format(date_range.end),
                }

                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
                df["parkingStartTime"] = pd.to_datetime(df["parkingStartTime"])
                df["parkingStopAt"] = pd.to_datetime(df["parkingStopAt"])
            except Exception as e:
                continue
        return df

    def _dt_ms_format(self, dt: datetime) -> str:
        return (
            dt.astimezone(timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z")
        )


if __name__ == "__main__":
    date_range = DateRange(start=datetime(2025, 8, 1), end=datetime.now())
    parkone_api = ParkOneAPI(date_range=date_range)
    response = parkone_api.get_all_parkings()
    print(response.head())

    print(response.dtypes)
