from datetime import datetime, timezone
import pandas as pd
import requests
from dotenv import load_dotenv
import os
from urllib.parse import urljoin

# from utils import DateRange

from webscraper.utils import DateRange

# Documentation: https://external-gw-staging.easyparksystem.net/api/swagger-ui/index.html#/authentication-resource/getJ%20wtUsingPOST


class EasyParkAPI:
    def __init__(self) -> None:
        load_dotenv()
        self.username = os.getenv("EASYPARK_USERNAME")
        self.password = os.getenv("EASYPARK_PASSWORD")
        self._tokens = self._get_tokens()
        self.id_token = self._tokens.get("idToken")
        self.refresh_token = self._tokens.get("refreshToken")

    def _get_tokens(self) -> dict:
        url = "https://sso.easyparksystem.net/api/login"

        response = requests.post(
            url,
            json={
                "userName": self.username,
                "password": self.password,
            },
        )
        response.raise_for_status()
        id_token = response.json().get("idToken", "")
        refresh_token = response.json().get("refreshToken", "")
        return {"idToken": id_token, "refreshToken": refresh_token}

    def get_parking(self, date_range: DateRange):
        base_url = "https://external-gw.easyparksystem.net/"
        endpoint = "api/export/operator-parkings-standard"
        url = urljoin(base_url, endpoint)

        headers = {
            "X-Authorization": f"Bearer {self.id_token}",
            "Content-Type": "application/json",
        }

        params = {
            "from": date_range.start.strftime("%Y-%m-%d"),
            "to": date_range.end.strftime("%Y-%m-%d"),
            "operatorId": 3340,
        }

        response = requests.get(
            url,
            headers=headers,
            params=params,
        )

        response.raise_for_status()
        data = response.json()

        return pd.DataFrame(data)


if __name__ == "__main__":
    api = EasyParkAPI()
    date_range = DateRange(
        start=datetime(2024, 1, 1),
        end=datetime(2024, 1, 2),
    )
    data = api.get_parking(date_range)
    print(data.head())

    print(data.dtypes)
