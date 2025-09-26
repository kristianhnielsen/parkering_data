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
    description: Mapped[str] = mapped_column(nullable=True)
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
    end_date_utc: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    price: Mapped[int]
    license_plate: Mapped[str]
    payment_start_utc: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    payment_end_utc: Mapped[Optional[datetime]] = mapped_column(nullable=True)
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
    start_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    rate_type: Mapped[str] = mapped_column(nullable=True)
    discount_code: Mapped[str] = mapped_column(nullable=True)
    discount_type: Mapped[str] = mapped_column(nullable=True)

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
    note: Mapped[str] = mapped_column(nullable=True)

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
