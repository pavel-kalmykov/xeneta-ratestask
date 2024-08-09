from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from rates_api import models, usecases
from rates_api.database import engine, get_db, run_migrations
from rates_api.exceptions import PortOrRegionNotFoundException
from rates_api.logging import logger
from rates_api.models import GetRatesParams

models.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app_: FastAPI):
    logger.info("Starting up...")
    logger.info("run alembic upgrade head...")
    run_migrations()
    logger.info("migrations successfully run")
    yield
    logger.info("Shutting down...")


app = FastAPI(lifespan=lifespan)


@app.exception_handler(ValidationError)
async def validation_error_handler(_: Request, exc: ValidationError):
    raise RequestValidationError(exc.errors())


@app.exception_handler(PortOrRegionNotFoundException)
def handle_port_not_found(_: Request, exc: PortOrRegionNotFoundException):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Could not find port/region: {exc.port_name}",
    )


@app.get("/rates")
async def get_rates(
    params: Annotated[GetRatesParams, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    return usecases.get_average_prices(db, params)
