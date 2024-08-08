from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session

from rates_api.models import DailyPrice


def get_average_prices(
    db: Session, date_from: date, date_to: date, origin: str, destination: str
) -> list[DailyPrice]:
    with open("db_scripts/rates-query.sql") as f:
        query = text(f.read())
    result = db.execute(
        query,
        {
            "origin": origin,
            "destination": destination,
            "date_from": date_from,
            "date_to": date_to,
            "min_prices_per_day": 3,
        },
    )

    return [DailyPrice(day=row.day, average_price=row.average_price) for row in result]
