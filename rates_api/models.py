from datetime import date

from pydantic import BaseModel
from sqlalchemy import Column, Date, ForeignKey, Integer, String

from rates_api.database import Base


class Region(Base):
    __tablename__ = "regions"

    slug = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    parent_slug = Column(String, ForeignKey("regions.slug"))


class Port(Base):
    __tablename__ = "ports"

    code = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    parent_slug = Column(String, ForeignKey("regions.slug"))


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    orig_code = Column(String, ForeignKey("ports.code"))
    dest_code = Column(String, ForeignKey("ports.code"))
    day = Column(Date, nullable=False)
    price = Column(Integer, nullable=False)


class DailyPrice(BaseModel):
    day: date
    average_price: int | None
