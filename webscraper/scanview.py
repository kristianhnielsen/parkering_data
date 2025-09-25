from dataclasses import dataclass, field
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import requests
import pandas as pd
import logging
from urllib.parse import urljoin
from dotenv import load_dotenv
import os
import numpy as np


@dataclass
class Credentials:
    username: str
    password: str


@dataclass
class DateRange:
    start: datetime
    end: datetime

    def days(self) -> int:
        return (self.end - self.start).days

    def split(self, interval_days: int) -> list["DateRange"]:
        ranges = []
        current_start = self.start
        while current_start < self.end:
            current_end = min(current_start + timedelta(days=interval_days), self.end)
            ranges.append(DateRange(current_start, current_end))
            current_start = current_end + timedelta(days=1)
        return ranges


@dataclass
class FetchPayload:
    date_from: datetime
    date_to: datetime
    start_record: int = 0
    length: int = 4000
    draw: int = 1
    columns: list[str] = field(
        default_factory=[
            "OrderDate",
            "Customer",
            "Name",
            "LocationName",
            "StartDate",
            "EndDate",
            "OrderStatus",
            "LicensePlates",
            "PaymentMethodName",
            "Price",
            "",
        ]
    )

    def to_dict(self) -> dict:
        payload = {
            "draw": self.draw,
            "order[0][column]": 0,
            "order[0][dir]": "asc",
            "start": self.start_record,
            "length": self.length,
            "search[value]": "",
            "search[regex]": "false",
            "Location": "",
            "DateFrom": self.date_from.strftime("%Y-%m-%d"),
            "DateTo": self.date_to.strftime("%Y-%m-%d"),
        }
        for idx, col in enumerate(self.columns):
            payload[f"columns[{idx}][data]"] = col
            payload[f"columns[{idx}][name]"] = ""
            payload[f"columns[{idx}][searchable]"] = "true"
            payload[f"columns[{idx}][orderable]"] = "true"
            payload[f"columns[{idx}][search][value]"] = ""
            payload[f"columns[{idx}][search][regex]"] = "false"
        return payload


class DriverManager:
    @staticmethod
    def create(
        headless: bool = False, start_maximized: bool = True
    ) -> webdriver.Chrome:
        options = Options()
        if start_maximized:
            options.add_argument("--start-maximized")
        if headless:
            options.add_argument("--headless")
        service = Service()
        return webdriver.Chrome(service=service, options=options)


class ScanviewSession:
    def __init__(self, creds: Credentials, driver: webdriver.Chrome):
        self.session = requests.Session()
        self.creds = creds
        self.driver = driver

    def login(self) -> None:
        # implement login via Selenium (navigate, fill creds, submit)
        """Log in to the ScanviewPay admin panel."""
        username_input = self.driver.find_element(By.ID, "Email")
        password_input = self.driver.find_element(By.ID, "Password")
        username_input.send_keys(self.creds.username)
        password_input.send_keys(self.creds.password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(2)  # Wait for login to complete

    def _get_cookies(self):
        return self.driver.get_cookies()

    def set_cookies(self):
        for cookie in self._get_cookies():
            self.session.cookies.set(
                cookie["name"],
                cookie["value"],
                domain=cookie.get("domain"),
                path=cookie.get("path"),
            )


class BaseDataFetcher:
    endpoint: str
    columns: list[str]
    base_url = "https://admin.scanviewpay.dk/"

    def __init__(self, session: ScanviewSession, date_range: DateRange):
        self.session = session
        self.date_range = date_range
        self.headers = {
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": self.base_url,
            "Referer": urljoin(self.base_url, self.endpoint.replace("/GetAll", "")),
            "X-Requested-With": "XMLHttpRequest",
        }

        self.session.driver.get(self.base_url)
        if self.session.driver.current_url != self.base_url:
            self.session.login()
        self.session.set_cookies()
        self.url = urljoin(self.base_url, self.endpoint)

    def total_records(self) -> int:
        payload = FetchPayload(
            date_from=self.date_range.start,
            date_to=self.date_range.end,
            columns=self.columns,
        ).to_dict()

        response = self.session.session.post(
            url=self.url,
            data=payload,
            headers=self.headers,
        )

        resp_json = response.json()
        return resp_json.get("iTotalRecords", 0)

    def fetch(self) -> pd.DataFrame:
        """Fetch the data for /Order"""

        data_df = pd.DataFrame()
        # don't split the requests into smaller date ranges,
        # if the total number of records can fit in a single request
        if self.total_records() <= FetchPayload.length:
            payload = FetchPayload(
                date_from=self.date_range.start,
                date_to=self.date_range.end,
                columns=self.columns,
            ).to_dict()

            response = self.session.session.post(
                url=self.url,
                data=payload,
                headers=self.headers,
            )
            data = response.json().get("aaData", [])
            data_df = pd.DataFrame(data)

        # If cannot fetch all data in one request,
        # divide it into ranges of interval_days.
        # interval_days = 10 should never exceed the max payload length of 4000
        for dr in self.date_range.split(interval_days=10):
            payload = FetchPayload(
                date_from=dr.start,
                date_to=dr.end,
                columns=self.columns,
            ).to_dict()
            resp = self.session.session.post(
                url=self.url,
                data=payload,
                headers=self.headers,
            )
            date_range_data = resp.json().get("aaData", [])
            date_range_data = pd.DataFrame(date_range_data)

            data_df = pd.concat([data_df, date_range_data], ignore_index=True)

        for column in set(
            self._columns_containing(data_df, "date")
            + self._columns_containing(data_df, "utc"),
        ):
            data_df[column] = self._col_to_datetime(data_df[column])

        for column in self._columns_containing(data_df, "id"):
            data_df[column] = data_df[column].astype(int)

        return data_df.drop_duplicates()

    def _col_to_datetime(self, df_col: pd.Series):
        return pd.to_datetime(
            df_col.str.extract(r"\((\d+)\)")[0].astype(np.int64, errors="ignore"),
            unit="ms",
        )

    def _columns_containing(self, df: pd.DataFrame, keyword: str) -> list[str]:
        return [col for col in df.columns.tolist() if keyword.lower() in col.lower()]


class PaymentDataFetcher(BaseDataFetcher):
    endpoint = "/Order/GetAll"
    columns = [
        "OrderDate",
        "Customer",
        "Name",
        "LocationName",
        "StartDate",
        "EndDate",
        "OrderStatus",
        "LicensePlates",
        "PaymentMethodName",
        "Price",
        "",
    ]


class ParkingLogFetcher(BaseDataFetcher):
    endpoint = "/ParkingLog/GetAll"
    columns = [
        "CreatedDateUtc",
        "EndDateUtc",
        "PaymentStartUtc",
        "PaymentEndUtc",
        "LicensePlate",
        "HandleByType",
        "Price",
        "AreaName",
        "",
    ]


class ScanviewScraper:
    def __init__(
        self, creds: Credentials, date_range: DateRange, headless: bool = False
    ):
        self.driver = DriverManager.create(headless=headless)
        self.session = ScanviewSession(creds, self.driver)
        self.date_range = date_range

    def get_payment_data(self) -> pd.DataFrame:
        fetcher = PaymentDataFetcher(self.session, self.date_range)
        return fetcher.fetch()

    def get_parking_logs(self) -> pd.DataFrame:
        fetcher = ParkingLogFetcher(self.session, self.date_range)
        return fetcher.fetch()


# Usage example:
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    creds = Credentials(
        username=os.getenv("SCANVIEW_USER"), password=os.getenv("SCANVIEW_PASSWORD")
    )
    date_range = DateRange(start=datetime(2025, 5, 1), end=datetime.now())
    scraper = ScanviewScraper(creds, date_range, headless=False)
    payments = scraper.get_payment_data()
    print(f"Rows of payments: {len(payments)}")
    print(payments.info())
