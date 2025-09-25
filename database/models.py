from datetime import datetime
from typing import Optional
import pandas as pd
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, DeclarativeBase, relationship, mapped_column


class Base(DeclarativeBase):
    pass
