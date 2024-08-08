from sqlalchemy import text
from sqlalchemy.orm import Session

from rates_api.config import settings
from rates_api.exceptions import PortOrRegionNotFoundException
from rates_api.logging import logger
from rates_api.models import DailyPrice, GetRatesParams


# Check commit message for more info
def validate_origin_and_destiny(db: Session, get_rate_params: GetRatesParams):
    logger.debug(
        f"Validating {get_rate_params.origin=} and {get_rate_params.destination=}"
    )
    with open("db_scripts/origin_and_destination_validation.sql") as f:
        query = text(f.read())
    result = db.execute(
        query,
        {
            "origin": get_rate_params.origin,
            "destination": get_rate_params.destination,
        },
    ).first()
    if result.origin_matches == 0:
        logger.warning(
            f"PortOrRegionNotFoundException for origin: {get_rate_params.origin}"
        )
        raise PortOrRegionNotFoundException(get_rate_params.origin)
    if result.destination_matches == 0:
        logger.warning(
            f"PortOrRegionNotFoundException for destination: {get_rate_params.destination}"
        )
        raise PortOrRegionNotFoundException(get_rate_params.destination)


def get_average_prices(
    db: Session, get_rate_params: GetRatesParams
) -> list[DailyPrice]:
    validate_origin_and_destiny(db, get_rate_params)
    with open("db_scripts/daily_price_rates.sql") as f:
        query = text(f.read())

    logger.debug(
        f"Executing rates query with {get_rate_params.model_dump_json()=}",
    )
    result = db.execute(
        query,
        {
            "origin": get_rate_params.origin,
            "destination": get_rate_params.destination,
            "date_from": get_rate_params.date_from,
            "date_to": get_rate_params.date_to,
            "min_prices_per_day": settings.min_prices_per_day,
        },
    )

    return [DailyPrice(day=row.day, average_price=row.average_price) for row in result]
