from dotenv import load_dotenv
from dataclasses import dataclass, field
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import requests
import pandas as pd
from urllib.parse import urljoin
from dotenv import load_dotenv
import json
from webscraper.utils import Credentials, DateRange, DriverManager, EnvManager


@dataclass
class FetchPayload:
    date_from: datetime
    date_to: datetime
    operatorId: str = "vejle"
    pageIndex: int = 0
    pageSize: int = 100_000_000

    parameters: list[dict] = field(
        default_factory=lambda: [
            {"id": "timeRange", "valueObject": ""},
            {"id": "payer", "value": None},
            {"id": "zone", "value": None},
            {"id": "paymentMethod", "value": None},
        ]
    )

    def _dates_to_time_range(self):
        sample_time_range = (
            '{"variant":"TIME_RANGE_FROM_TO","from":"2025-09-16","to":"2025-09-18"}'
        )
        time_range = json.loads(sample_time_range)
        time_range["from"] = self.date_from.strftime("%Y-%m-%d")
        time_range["to"] = self.date_to.strftime("%Y-%m-%d")
        time_range_str = json.dumps(time_range)

        return time_range_str

    def to_dict(self) -> dict:
        self.parameters[0]["valueObject"] = self._dates_to_time_range()
        payload = {
            "operatorId": self.operatorId,
            "pageIndex": self.pageIndex,
            "pageSize": self.pageSize,
            "parameters": self.parameters,
        }
        return payload


class GiantleapSession:
    def __init__(self, creds: Credentials, driver: webdriver.Chrome):
        self.session = requests.Session()
        self.creds = creds
        self.driver = driver

    def login(self) -> None:
        # implement login via Selenium (navigate, fill creds, submit)
        """Log in to the Giantleap admin panel."""

        username_input = self.driver.find_element(
            By.CSS_SELECTOR, "input[placeholder='Brugernavn..']"
        )
        password_input = self.driver.find_element(
            By.CSS_SELECTOR, "input[placeholder='adgangskode..']"
        )

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


class DataFetcher:
    base_url = "https://vejle-permit.giantleap.no"
    login_url = urljoin(base_url, "admin.html#/login")
    reports_url = urljoin(base_url, "admin.html#/dynamic-report/payment-txn-report")

    endpoint = urljoin(
        base_url,
        "api/admin/reports/payment-txn-report/preview.json",
    )

    def __init__(self, session: GiantleapSession, date_range: DateRange):
        self.session = session
        self.date_range = date_range
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "da-DK,da;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/json; charset=UTF-8",
            "Origin": self.base_url,
            "Referer": urljoin(self.base_url, "admin.html"),
            "Sec-Ch-Ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        }

        self.session.driver.get(self.login_url)
        time.sleep(2)
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

    def _get_x_token(self) -> str:
        local_storage = self._get_local_storage()
        # The key for the token may vary, so you might need to inspect the
        # browser's Local Storage or network traffic to find the correct key.
        x_token_raw: str = local_storage.get("accessToken_admin", "")
        x_token: dict = json.loads(x_token_raw)
        return x_token.get("value", "")

    def fetch(self) -> pd.DataFrame:
        """Fetch the data for /Order"""
        self.session.driver.get(self.reports_url)
        x_token = self._get_x_token()
        self.headers["X-Token"] = x_token

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
        columns = [
            col.replace("label.", "").replace(".", "_").strip()
            for col in resp_json["headers"]["columns"]
        ]
        data = [row["columns"] for row in resp_json["rows"]]
        df = pd.DataFrame(data=data, columns=columns)
        df["amount"] = (
            df["amount"].str.replace(",", ".").str.replace(" ", "").astype(float)
        )
        df["vat"] = df["vat"].str.replace(",", ".").str.replace(" ", "").astype(float)
        df["report_time"] = pd.to_datetime(
            df["report_time"], format="mixed", dayfirst=True
        )

        df["payer"] = df["payer"].str.replace("  ", " ").str.strip()

        return df


class GiantleapScraper:
    def __init__(
        self, creds: Credentials, date_range: DateRange, headless: bool = False
    ):
        self.driver = DriverManager.create(headless=headless)
        self.session = GiantleapSession(creds, self.driver)
        self.date_range = date_range

    def fetch(self) -> pd.DataFrame:
        data = DataFetcher(self.session, self.date_range).fetch()
        return data


if __name__ == "__main__":
    load_dotenv()
    pd.options.display.max_rows = None
    pd.options.display.max_columns = None
    pd.options.display.max_colwidth = None
    creds = Credentials(
        username=EnvManager.get("GIANTLEAP_USER"),
        password=EnvManager.get("GIANTLEAP_PASSWORD"),
    )
    giantleap = GiantleapSession(creds, DriverManager.create(headless=True))

    time.sleep(5)  # Wait for login to complete

    data_fetcher = DataFetcher(
        giantleap, DateRange(start=datetime(2025, 8, 28), end=datetime.now())
    )
    data = data_fetcher.fetch()
    print(data.head())
    print(data.info())
    time.sleep(2)
