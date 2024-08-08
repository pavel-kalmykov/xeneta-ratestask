from sqlalchemy import text
from sqlalchemy.orm import Session

from rates_api.models import DailyPrice, GetRatesParams


def get_average_prices(
    db: Session, get_rate_params: GetRatesParams
) -> list[DailyPrice]:
    with open("db_scripts/rates-query.sql") as f:
        query = text(f.read())
    result = db.execute(
        query,
        {
            "origin": get_rate_params.origin,
            "destination": get_rate_params.destination,
            "date_from": get_rate_params.date_from,
            "date_to": get_rate_params.date_to,
            "min_prices_per_day": 3,
        },
    )

    return [DailyPrice(day=row.day, average_price=row.average_price) for row in result]
