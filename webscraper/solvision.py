import os
from dotenv import load_dotenv
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
    meters: list[int] = field(
        default_factory=lambda: [
            17,
            18,
            14,
            11,
            1,
            2,
            3,
            4,
            5,
            13,
            25,
            26,
            27,
            28,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            10,
            16,
            9,
            15,
            22,
            29,
            19,
            8,
        ]
    )

    def to_dict(self) -> dict:
        payload = {
            "Start": self.date_from.strftime("%Y-%m-%dT%H:%M:00.000Z"),
            "End": self.date_to.strftime("%Y-%m-%dT%H:%M:00.000Z"),
            "Meters": self.meters,
        }
        return payload


class SolvisionSession:
    def __init__(self, creds: Credentials, driver: webdriver.Chrome):
        self.session = requests.Session()
        self.creds = creds
        self.driver = driver

    def login(self) -> None:
        # implement login via Selenium (navigate, fill creds, submit)
        """Log in to the Solvision admin panel."""
        username_input = self.driver.find_element(By.ID, "username")
        password_input = self.driver.find_element(By.ID, "password")

        username_input.send_keys(self.creds.username)
        password_input.send_keys(self.creds.password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(2)  # Wait for login to complete

    def _get_cookies(self):
        return self.driver.get_cookies()

    def set_cookies(self):
        pass


class DataFetcher:
    base_url = "https://portal.solvision.dk"
    endpoint = "https://api.solvision.dk/mobilbase/api/v1/reports/transactions/72/0"
    transaction_url = urljoin(base_url, "statistics/transactions")
    columns: list[str] = [
        "id",
        "deviceName",
        "card",
        "paymentTime",
        "plate",
        "start",
        "end",
        "rateType",
        "discountCode",
        "discountType",
        "cardFirm",
        "cardCount",
        "amount",
        "fee",
        "parkingTime",
    ]

    def __init__(self, session: SolvisionSession, date_range: DateRange):
        self.session = session
        self.date_range = date_range
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "da-DK,da;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/json; charset=UTF-8",
            "Origin": self.base_url,
            "Priority": "u=1, i",
            "Referer": self.base_url,
            "Sec-Ch-Ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        }

        self.session.driver.get(self.base_url)
        self.session.login()
        self.session.set_cookies()

    def _get_local_storage(self) -> dict:
        local_storage = self.session.driver.execute_script(
            """
            let store = {};
            for (let i = 0; i < window.localStorage.length; i++) {
                let key = window.localStorage.key(i);
                store[key] = window.localStorage.getItem(key);
            }
            return store;
        """
        )
        return local_storage

    def fetch(self) -> pd.DataFrame:
        """Fetch the data for /Order"""
        self.session.driver.get(self.transaction_url)
        local_storage = self.session.driver.execute_script(
            """
            let store = {};
            for (let i = 0; i < window.localStorage.length; i++) {
                let key = window.localStorage.key(i);
                store[key] = window.localStorage.getItem(key);
            }
            return store;
        """
        )
        token = local_storage.get("token")

        self.headers["Authorization"] = f"Bearer {token}"

        payload = FetchPayload(
            date_from=self.date_range.start,
            date_to=self.date_range.end,
        ).to_dict()

        response = self.session.session.post(
            url=self.endpoint,
            json=payload,
            headers=self.headers,
        )

        resp_json = response.json()
        data = resp_json["result"].get("data")
        data_df = pd.DataFrame(data)

        # Convert date columns to datetime
        date_columns = ["paymentTime", "start", "end"]
        for col in date_columns:
            data_df[col] = pd.to_datetime(data_df[col])

        return data_df


class SolvisionScraper:
    def __init__(
        self, creds: Credentials, date_range: DateRange, headless: bool = False
    ):
        self.driver = DriverManager.create(headless=headless)
        self.session = SolvisionSession(creds, self.driver)
        self.date_range = date_range

    def fetch(self) -> pd.DataFrame:
        data = DataFetcher(self.session, self.date_range).fetch()
        return data


if __name__ == "__main__":
    load_dotenv()
    base_url = "https://portal.solvision.dk/"

    creds = Credentials(
        username=os.getenv("SOLVISION_USER"), password=os.getenv("SOLVISION_PASSWORD")
    )
    solvision = SolvisionSession(creds, DriverManager.create(headless=False))

    time.sleep(5)  # Wait for login to complete

    # Navigate to the desired page
    data_fetcher = DataFetcher(
        solvision, DateRange(start=datetime(2025, 8, 28), end=datetime.now())
    )
    data = data_fetcher.fetch()
    pd.options.display.max_columns = None
    print(data.head())
    print(data.info())
    time.sleep(2)
