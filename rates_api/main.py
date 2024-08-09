from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from rates_api import models, usecases
from rates_api.database import engine, get_db, run_migrations
from rates_api.exceptions import PortOrRegionNotFoundException
from rates_api.logging import logger
from rates_api.models import DailyPriceStats, GetRatesParams

models.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Starting up...")
    logger.info("run alembic upgrade head...")
    run_migrations()
    logger.info("migrations successfully run")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Rates API",
    description="An API for querying shipment rates",
    version="1.0",
    lifespan=lifespan,
)


@app.exception_handler(ValidationError)
async def validation_error_handler(_: Request, exc: ValidationError):
    raise RequestValidationError(exc.errors())


@app.exception_handler(PortOrRegionNotFoundException)
def handle_port_not_found(_: Request, exc: PortOrRegionNotFoundException):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Could not find port/region: {exc.port_name}",
    )


@app.get("/", include_in_schema=False)
def main():
    return RedirectResponse("/docs", status_code=status.HTTP_308_PERMANENT_REDIRECT)


@app.get(
    "/rates",
    tags=["Rates"],
    description=(
        "This endpoint takes the specified parameters and returns a list with the "
        "average prices for each day on a route between _origin_ and _destination_. "
        "For days on which there are less than 3 prices in total, it returns null.\n"
        "\n"
        "Both the _origin_, _destination_ params accept either port codes or region "
        "slugs, making it possible to query for average prices per day between "
        "geographic groups of ports.\n"
    ),
    response_description="List of daily price statistics",
)
def get_rates(
    params: Annotated[GetRatesParams, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> list[DailyPriceStats]:
    return usecases.get_average_prices(db, params)
