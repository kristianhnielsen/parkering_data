from datetime import datetime
import os
from dotenv import load_dotenv
import database.operations as db_ops
from webscraper.easypark import EasyParkAPI
from webscraper.giantleap import GiantleapScraper
from webscraper.parkone import ParkOneAPI
from webscraper.scanview import ScanviewScraper
from database.models import (
    EasyParkParking,
    GiantleapOrder,
    Logs,
    ParkOneParking,
    ParkParkParking,
    ScanviewPayment,
    ScanviewLog,
    SolvisionOrder,
)
from webscraper.solvision import SolvisionScraper
from webscraper.parkpark import ParkParkAPI
from webscraper.utils import Credentials, DateRange, EnvManager


def get_scanview(date_range: DateRange):
    # Initialize credentials and date range
    creds = Credentials(
        username=EnvManager.get("SCANVIEW_USERNAME"),
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
        username=EnvManager.get("SOLVISION_USERNAME"),
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
        username=EnvManager.get("GIANTLEAP_USERNAME"),
        password=EnvManager.get("GIANTLEAP_PASSWORD"),
    )
    data_fetcher = GiantleapScraper(creds, date_range, headless=True)
    data = data_fetcher.fetch()

    giantleap_data = [GiantleapOrder(order=order) for _, order in data.iterrows()]
    print(f"Fetched {len(giantleap_data)} Giantleap orders")

    return giantleap_data


def get_parkpark(date_range: DateRange):
    api_key = EnvManager.get("PARKPARK_API_KEY")
    parkpark_api = ParkParkAPI(api_key, date_range)
    parking_data = parkpark_api.fetch_parkings()
    parkpark_data = [ParkParkParking(entry) for _, entry in parking_data.iterrows()]
    print(f"Fetched {len(parkpark_data)} ParkPark parking entries")
    return parkpark_data


def get_parkone(date_range: DateRange):
    parkone_api = ParkOneAPI(date_range)
    parking_data = parkone_api.get_all_parkings()
    parkone_data = [ParkOneParking(entry) for _, entry in parking_data.iterrows()]
    print(f"Fetched {len(parkone_data)} ParkOne parking entries")
    return parkone_data


def get_easypark(date_range: DateRange):
    easypark_api = EasyParkAPI()
    easypark_data = easypark_api.get_parking(date_range)
    easypark_data = [EasyParkParking(entry) for _, entry in easypark_data.iterrows()]
    print(f"Fetched {len(easypark_data)} EasyPark parking entries")
    return easypark_data


def main():
    load_dotenv()
    tables = []
    date_range = DateRange(start=datetime(2025, 9, 20), end=datetime.now())
    run_time = datetime.now()

    # Track counts and errors for each data source
    entry_counts = {
        "scanview_payment_entries": 0,
        "scanview_log_entries": 0,
        "solvision_order_entries": 0,
        "giantleap_order_entries": 0,
        "parkpark_entries": 0,
        "parkone_entries": 0,
        "easypark_entries": 0,
    }
    errors = []

    try:
        # Get Scanview data
        try:
            scanview_orders, scanview_logs = get_scanview(date_range)
            tables.append(scanview_orders)
            tables.append(scanview_logs)
            entry_counts["scanview_payment_entries"] = len(scanview_orders)
            entry_counts["scanview_log_entries"] = len(scanview_logs)
        except Exception as e:
            errors.append(f"Scanview: {str(e)}")
            print(f"Error fetching Scanview data: {e}")

        # Get Solvision data
        try:
            solvision_orders = get_solvision(date_range)
            tables.append(solvision_orders)
            entry_counts["solvision_order_entries"] = len(solvision_orders)
        except Exception as e:
            errors.append(f"Solvision: {str(e)}")
            print(f"Error fetching Solvision data: {e}")

        # Get Giantleap data
        try:
            giantleap_orders = get_giantleap(date_range)
            tables.append(giantleap_orders)
            entry_counts["giantleap_order_entries"] = len(giantleap_orders)
        except Exception as e:
            errors.append(f"Giantleap: {str(e)}")
            print(f"Error fetching Giantleap data: {e}")

        # Get ParkPark data
        try:
            parkpark_overview = get_parkpark(date_range)
            tables.append(parkpark_overview)
            entry_counts["parkpark_entries"] = len(parkpark_overview)
        except Exception as e:
            errors.append(f"ParkPark: {str(e)}")
            print(f"Error fetching ParkPark data: {e}")

        # Get ParkOne data
        try:
            parkone_data = get_parkone(date_range)
            tables.append(parkone_data)
            entry_counts["parkone_entries"] = len(parkone_data)
        except Exception as e:
            errors.append(f"ParkOne: {str(e)}")
            print(f"Error fetching ParkOne data: {e}")

        # Get EasyPark data
        try:
            easypark_data = get_easypark(date_range)
            tables.append(easypark_data)
            entry_counts["easypark_entries"] = len(easypark_data)
        except Exception as e:
            errors.append(f"EasyPark: {str(e)}")
            print(f"Error fetching EasyPark data: {e}")

        # Determine overall status
        if errors:
            status = "PARTIAL_SUCCESS" if any(entry_counts.values()) else "FAILED"
            message = "Errors occurred: " + "; ".join(errors)
        else:
            status = "SUCCESS"
            message = "Successfully fetched all data"

        # Create log entry
        runtime = (datetime.now() - run_time).total_seconds()
        log_entry = Logs(
            run_time=run_time,
            date_range_from=date_range.start,
            date_range_to=date_range.end,
            scanview_payment_entries=entry_counts["scanview_payment_entries"],
            scanview_log_entries=entry_counts["scanview_log_entries"],
            solvision_order_entries=entry_counts["solvision_order_entries"],
            giantleap_order_entries=entry_counts["giantleap_order_entries"],
            parkpark_entries=entry_counts["parkpark_entries"],
            parkone_entries=entry_counts["parkone_entries"],
            easypark_entries=entry_counts["easypark_entries"],
            status=status,
            message=message,
            runtime_seconds=runtime,
        )

        # Store data in the database
        with db_ops.get_db() as db:
            for table in tables:
                db.add_all(table)
            db.add(log_entry)

        # Raise exception if all sources failed
        if status == "FAILED":
            raise Exception(message)

    except Exception as e:
        # Create failure log entry if not already created
        runtime = (datetime.now() - run_time).total_seconds()
        log_entry = Logs(
            run_time=run_time,
            date_range_from=date_range.start,
            date_range_to=date_range.end,
            scanview_payment_entries=entry_counts["scanview_payment_entries"],
            scanview_log_entries=entry_counts["scanview_log_entries"],
            solvision_order_entries=entry_counts["solvision_order_entries"],
            giantleap_order_entries=entry_counts["giantleap_order_entries"],
            parkpark_entries=entry_counts["parkpark_entries"],
            parkone_entries=entry_counts["parkone_entries"],
            easypark_entries=entry_counts["easypark_entries"],
            status="FAILED",
            message=str(e),
            runtime_seconds=runtime,
        )

        with db_ops.get_db() as db:
            db.add(log_entry)

        raise


if __name__ == "__main__":
    main()
    print("Done")
