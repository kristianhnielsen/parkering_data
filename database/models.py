from datetime import datetime
from typing import Optional
import pandas as pd
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column
from database.utils import safe_na_datetime


class Base(DeclarativeBase):
    pass


class Scanview(Base):
    __tablename__ = "scanview"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    date: Mapped[datetime]
    type: Mapped[str]
    description: Mapped[Optional[str]]
    subscription_name: Mapped[str]
    start_date: Mapped[datetime]
    end_date: Mapped[datetime]
    status: Mapped[str]
    license_plate: Mapped[str]
    customer: Mapped[str]
    location_id: Mapped[int]
    location_name: Mapped[str]
    payment_method: Mapped[int]
    payment_method_name: Mapped[str]
    auto_renew: Mapped[bool]
    price: Mapped[int]

    def __init__(self, order: pd.Series):
        super().__init__()
        self.date = order.OrderDate
        self.type = order.Name
        self.description = order.Description
        self.subscription_name = order.SubscriptionName
        self.start_date = order.StartDate
        self.end_date = order.EndDate
        self.status = order.OrderStatus
        self.license_plate = order.LicensePlates
        self.customer = order.Customer
        self.location_id = order.LocationID
        self.location_name = order.LocationName
        self.payment_method = order.PaymentMethod
        self.payment_method_name = order.PaymentMethodName
        self.auto_renew = order.AutoRenew
        self.price = order.Price


class ScanviewLog(Base):
    __tablename__ = "scanview_log"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    area_name: Mapped[str]
    area_id: Mapped[int]
    created_date_utc: Mapped[datetime]
    end_date_utc: Mapped[Optional[datetime]]
    price: Mapped[int]
    license_plate: Mapped[str]
    payment_start_utc: Mapped[Optional[datetime]]
    payment_end_utc: Mapped[Optional[datetime]]
    handle: Mapped[bool]
    handle_by_type: Mapped[str]
    handle_by: Mapped[str]

    def __init__(self, log: pd.Series):
        super().__init__()
        log = safe_na_datetime(log)
        self.area_name = log.AreaName
        self.area_id = int(log.AreaNo)
        self.created_date_utc = log.CreatedDateUtc
        self.end_date_utc = log.EndDateUtc
        self.price = log.Price
        self.license_plate = log.LicensePlate
        self.payment_start_utc = log.PaymentStartUtc
        self.payment_end_utc = log.PaymentEndUtc
        self.handle = log.Handle
        self.handle_by_type = log.HandleByType
        self.handle_by = log.HandleBy


class Solvision(Base):
    __tablename__ = "solvision"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    location_id: Mapped[int]
    location: Mapped[str]
    card: Mapped[str]
    card_firm: Mapped[str]
    card_count: Mapped[int]
    price: Mapped[float]
    fee: Mapped[int]
    parking_time: Mapped[int]
    payment_time: Mapped[datetime]
    license_plate: Mapped[str]
    start_date: Mapped[Optional[datetime]]
    end_date: Mapped[Optional[datetime]]
    rate_type: Mapped[Optional[str]]
    discount_code: Mapped[Optional[str]]
    discount_type: Mapped[Optional[str]]

    def __init__(self, order: pd.Series):
        super().__init__()
        order = safe_na_datetime(order)
        self.location_id = order.id
        self.location = order.deviceName
        self.license_plate = order.plate
        self.start_date = order.start
        self.end_date = order.end
        self.price = order.amount
        self.fee = order.fee
        self.parking_time = order.parkingTime
        self.payment_time = order.paymentTime
        self.card = order.card
        self.card_firm = order.cardFirm
        self.card_count = order.cardCount
        self.rate_type = order.rateType
        self.discount_code = order.discountCode
        self.discount_type = order.discountType


class Giantleap(Base):
    __tablename__ = "giantleap"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    report_time: Mapped[datetime]
    description: Mapped[str]
    zone: Mapped[str]
    payer_phone: Mapped[str]
    payer_name: Mapped[str]
    amount: Mapped[float]
    vat: Mapped[float]
    payment_method: Mapped[str]
    payment_card: Mapped[str]
    payment_transaction: Mapped[int]
    note: Mapped[Optional[str]]

    def __init__(self, order: pd.Series):
        super().__init__()
        self.report_time = order.report_time
        self.description = order.item_description
        self.zone = order.zone
        self.payer_phone = order.payer_msisdn
        self.payer_name = order.payer
        self.amount = order.amount
        self.vat = order.vat
        self.payment_method = order.payment_method
        self.payment_card = order.payment_card
        self.payment_transaction = order.payment_transaction
        self.note = order.note


class ParkPark(Base):
    __tablename__ = "parkpark"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    parking_id: Mapped[int]
    external_id: Mapped[Optional[str]]
    zone_name: Mapped[Optional[str]]
    name: Mapped[str]
    license_plate_country: Mapped[str]
    license_plate: Mapped[str]
    checkin: Mapped[datetime]
    checkout: Mapped[datetime]
    minutes: Mapped[int]
    amount: Mapped[int]

    def __init__(self, parking: pd.Series):
        super().__init__()
        self.parking_id = parking.parking_id
        self.external_id = parking.external_id
        self.name = parking.zone_name
        self.zone_name = None if parking.zone_name == "" else parking.zone_name
        self.license_plate_country = parking.reg_cc.upper()
        self.license_plate = parking.reg.upper()
        self.checkin = datetime.strptime(parking.checkin, "%Y-%m-%d %H:%M:%S")
        self.checkout = datetime.strptime(parking.checkout, "%Y-%m-%d %H:%M:%S")
        self.minutes = parking.minutes
        self.amount = parking.amount


class ParkOne(Base):
    __tablename__ = "parkone"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    parkone_parking_id: Mapped[int]
    external_parking_id: Mapped[Optional[str]]
    parking_start_time: Mapped[datetime]
    parking_stop_at: Mapped[Optional[datetime]]
    vehicle_reg_id: Mapped[str]
    zone: Mapped[str]
    total_amount: Mapped[float]

    def __init__(self, parking: pd.Series):
        super().__init__()
        self.parking_start_time = parking.parkingStartTime
        self.parking_stop_at = parking.parkingStopAt
        self.vehicle_reg_id = parking.vehicleRegId
        self.zone = parking.zone
        self.total_amount = parking.totalAmount
        self.parkone_parking_id = parking.parkoneParkingId
        self.external_parking_id = parking.externalParkingId


class EasyPark(Base):
    __tablename__ = "easypark"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    area: Mapped[int]
    country: Mapped[str]
    start_date: Mapped[datetime]
    end_date: Mapped[datetime]
    license_plate: Mapped[str]
    fee_exclusive_vat: Mapped[Optional[float]]
    fee_inclusive_vat: Mapped[Optional[float]]
    fee_vat: Mapped[Optional[float]]
    currency: Mapped[str]
    parking_id: Mapped[int]
    stopped: Mapped[bool]
    source: Mapped[Optional[str]]
    subtype: Mapped[Optional[str]]
    spot: Mapped[Optional[str]]
    area_name: Mapped[str]
    external_transaction_id: Mapped[Optional[str]]

    def __init__(self, parking: pd.Series):
        super().__init__()
        # Preprocess datetimes
        parking = safe_na_datetime(parking)
        parking["startDate"] = parking["startDate"].split(".")[0].split("+")[0]
        parking["endDate"] = parking["endDate"].split(".")[0].split("+")[0]

        # Assign values
        self.area = parking["areaNo"]
        self.country = parking["areaCountryCode"]
        self.start_date = datetime.strptime(parking["startDate"], "%Y-%m-%dT%H:%M:%S")
        self.end_date = datetime.strptime(parking["endDate"], "%Y-%m-%dT%H:%M:%S")
        self.license_plate = parking["licenseNumber"]
        self.fee_exclusive_vat = parking["parkingFeeExclusiveVAT"]
        self.fee_inclusive_vat = parking["parkingFeeInclusiveVAT"]
        self.fee_vat = parking["parkingFeeVAT"]
        self.currency = parking["currency"]
        self.parking_id = parking["parkingId"]
        self.stopped = parking["stopped"]
        self.source = parking["sourceSystem"]
        self.subtype = parking["subType"]
        self.spot = parking["spotNumber"]
        self.area_name = parking["areaName"]
        self.external_transaction_id = parking["externalTransactionNumber"]


class Logs(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    run_time: Mapped[datetime]
    date_range_from: Mapped[datetime]
    date_range_to: Mapped[datetime]
    easypark_entries: Mapped[int]
    parkone_entries: Mapped[int]
    parkpark_entries: Mapped[int]
    scanview_entries: Mapped[int]
    scanview_log_entries: Mapped[int]
    solvision_entries: Mapped[int]
    giantleap_entries: Mapped[int]
    status: Mapped[str]
    message: Mapped[str]
    runtime_seconds: Mapped[float]

    def __init__(
        self,
        run_time: datetime,
        date_range_from: datetime,
        date_range_to: datetime,
        easypark_entries: int,
        parkone_entries: int,
        parkpark_entries: int,
        scanview_entries: int,
        scanview_log_entries: int,
        solvision_entries: int,
        giantleap_entries: int,
        status: str,
        message: str,
        runtime_seconds: float,
    ):
        super().__init__()
        self.run_time = run_time
        self.date_range_from = date_range_from
        self.date_range_to = date_range_to
        self.easypark_entries = easypark_entries
        self.parkone_entries = parkone_entries
        self.parkpark_entries = parkpark_entries
        self.scanview_entries = scanview_entries
        self.scanview_log_entries = scanview_log_entries
        self.solvision_entries = solvision_entries
        self.giantleap_entries = giantleap_entries
        self.status = status
        self.message = message
        self.runtime_seconds = runtime_seconds
