from datetime import date

from pydantic import BaseModel, model_validator
from sqlalchemy import Column, Date, ForeignKey, Integer, String

from rates_api.config import settings
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


class GetRatesParams(BaseModel):
    date_from: date
    date_to: date
    origin: str
    destination: str

    @model_validator(mode="after")
    def date_to_must_be_after_date_from(self):
        assert self.date_from <= self.date_to, "date_to must be after date_from"
        assert (
            (self.date_to - self.date_from).days < settings.max_days_interval
        ), f"[date_from-date_to] range must be less than {settings.max_days_interval} days"
