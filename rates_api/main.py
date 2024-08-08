from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from rates_api import models, usecases
from rates_api.database import engine, get_db
from rates_api.models import GetRatesParams

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    raise RequestValidationError(exc.errors())


@app.get("/rates")
async def get_rates(
    params: Annotated[GetRatesParams, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    return usecases.get_average_prices(db, params)
