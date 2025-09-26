from datetime import datetime
import os
from dotenv import load_dotenv
import database.operations as db_ops
from webscraper.giantleap import GiantleapScraper
from webscraper.scanview import ScanviewScraper
from database.models import GiantleapOrder, ScanviewPayment, ScanviewLog, SolvisionOrder
from webscraper.solvision import SolvisionScraper
from webscraper.utils import Credentials, DateRange, EnvManager


def get_scanview(date_range: DateRange):
    # Initialize credentials and date range
    creds = Credentials(
        username=EnvManager.get("SCANVIEW_USER"),
        password=EnvManager.get("SCANVIEW_PASSWORD"),
    )
    scanview_scraper = ScanviewScraper(creds, date_range, headless=True)

    # Fetch payment data
    scanview_payments = scanview_scraper.get_payment_data()
    scanview_orders = [
        ScanviewPayment(order=payment_order)
        for _, payment_order in scanview_payments.iterrows()
    ]
    print(f"Fetched {len(scanview_orders)} Scanview orders")

    # Fetch parking logs
    logs = scanview_scraper.get_parking_logs()
    scanview_logs = [
        ScanviewLog(log=scanview_log) for _, scanview_log in logs.iterrows()
    ]
    print(f"Fetched {len(scanview_logs)} Scanview logs")
    return scanview_orders, scanview_logs


def get_solvision(date_range: DateRange):
    creds = Credentials(
        username=EnvManager.get("SOLVISION_USER"),
        password=EnvManager.get("SOLVISION_PASSWORD"),
    )

    # time.sleep(5)  # Wait for login to complete

    data_scraper = SolvisionScraper(creds, date_range, headless=True)
    data = data_scraper.fetch()

    # Remove summary row
    total_row = data[data["cardFirm"] == "Total"]
    data.drop(total_row.index, inplace=True)

    solvision_data = [SolvisionOrder(order=order) for _, order in data.iterrows()]
    print(f"Fetched {len(solvision_data)} Solvision orders")

    return solvision_data


def get_giantleap(date_range: DateRange):
    creds = Credentials(
        username=EnvManager.get("GIANTLEAP_USER"),
        password=EnvManager.get("GIANTLEAP_PASSWORD"),
    )
    data_fetcher = GiantleapScraper(creds, date_range, headless=True)
    data = data_fetcher.fetch()

    giantleap_data = [GiantleapOrder(order=order) for _, order in data.iterrows()]
    print(f"Fetched {len(giantleap_data)} Giantleap orders")

    return giantleap_data


def main():
    load_dotenv()
    tables = []
    date_range = DateRange(start=datetime(2025, 9, 9), end=datetime.now())

    # Get Scanview data
    scanview_orders, scanview_logs = get_scanview(date_range)
    tables.append(scanview_orders)
    tables.append(scanview_logs)

    # Get Solvision data
    solvision_orders = get_solvision(date_range)
    tables.append(solvision_orders)

    # Get Giantleap data
    giantleap_orders = get_giantleap(date_range)
    tables.append(giantleap_orders)

    # Store data in the database
    with db_ops.get_db() as db:
        for table in tables:
            db.add_all(table)


if __name__ == "__main__":
    main()
    print("Done")
