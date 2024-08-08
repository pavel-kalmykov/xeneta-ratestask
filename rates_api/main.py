from datetime import date
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from rates_api import models, usecases
from rates_api.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/rates")
async def get_rates(
    date_from: date,
    date_to: date,
    origin: str,
    destination: str,
    db: Annotated[Session, Depends(get_db)],
):
    return usecases.get_average_prices(db, date_from, date_to, origin, destination)
