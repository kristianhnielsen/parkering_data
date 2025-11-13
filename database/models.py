from datetime import datetime
from typing import Optional
import pandas as pd
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column
from database.utils import safe_na_datetime


class Base(DeclarativeBase):
    pass


class ScanviewPayment(Base):
    __tablename__ = "scanview_payment"

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


class SolvisionOrder(Base):
    __tablename__ = "solvision_order"

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


class GiantleapOrder(Base):
    __tablename__ = "giantleap_order"

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


class ParkParkOverview(Base):
    __tablename__ = "parkpark_overview"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str]
    external_id: Mapped[Optional[str]]
    zone_name: Mapped[Optional[str]]
    count: Mapped[int]
    address: Mapped[str]
    zip: Mapped[int]
    city: Mapped[str]
    seconds: Mapped[int]
    minutes: Mapped[int]
    amount: Mapped[int]

    def __init__(self, overview: pd.Series):
        super().__init__()
        self.name = overview.name  # type: ignore
        self.external_id = overview.external_id
        self.zone_name = None if overview.zone_name == "" else overview.zone_name
        self.count = overview["count"]  # type: ignore
        self.address = overview.address
        self.zip = overview.zip
        self.city = overview.city
        self.seconds = overview.seconds
        self.minutes = overview.minutes
        self.amount = overview.amount


class ParkParkParking(Base):
    __tablename__ = "parkpark_parking"

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


class ParkOneParking(Base):
    __tablename__ = "parkone_all_parking"

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
