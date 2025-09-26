from dataclasses import dataclass
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


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
class Credentials:
    username: str | None
    password: str | None

    def __is_valid(self, credential: str | None):
        return isinstance(credential, str) and credential.strip() != ""

    def __post_init__(self) -> None:
        if not self.__is_valid(self.username) or not self.__is_valid(self.password):
            raise EnvironmentError(
                "One or more environment variables are not set correctly. Please check your .env file."
            )


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
