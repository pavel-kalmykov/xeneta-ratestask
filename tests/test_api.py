import pytest
from fastapi.testclient import TestClient

from rates_api.main import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_get_rates_example(client):
    """This checks that the sample invocation shown in the assignment works"""
    response = client.get(
        "/rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10  # 10 days of data
    assert all(isinstance(day["day"], str) for day in data)
    assert all(isinstance(day["average_price"], (int, type(None))) for day in data)

    day1 = data[0]
    assert day1["day"] == "2016-01-01"
    assert day1["average_price"] == 1112

    day3 = data[2]
    assert day3["day"] == "2016-01-03"
    assert day3["average_price"] is None

    # From here, values are assumed based on the provided data
    day4 = data[3]
    assert day4["day"] == "2016-01-04"
    assert day4["average_price"] is None  # Because count(prices) == 1 < 3

    day10 = data[9]
    assert day10["day"] == "2016-01-10"
    assert day10["average_price"] == 1124


def test_get_rates_missing_parameters(client):
    response = client.get("/rates")
    assert response.status_code == 422


def test_get_rates_incorrect_date_format(client):
    response = client.get(
        "/rates?date_from=yesterday&date_to=now&origin=CNSGH&destination=north_europe_main"
    )
    assert response.status_code == 422


def test_get_rates_incorrect_date_range(client):
    response = client.get(
        "/rates?date_from=2016-01-01&date_to=2015-01-10&origin=CNSGH&destination=north_europe_main"
    )
    assert response.status_code == 422
    data = response.json()
    assert "date_to must be after date_from" in data["detail"][0]["msg"]


def test_get_rates_too_large_date_range(client):
    response = client.get(
        "/rates?date_from=2016-01-01&date_to=2016-02-10&origin=CNSGH&destination=north_europe_main"
    )
    assert response.status_code == 422
    data = response.json()
    assert "[date_from-date_to] range must be less than" in data["detail"][0]["msg"]


def test_get_rates_wrong_origin(client):
    response = client.get(
        "/rates?date_from=2016-01-01&date_to=2016-01-10&origin=MYHOUSE&destination=north_europe_main"
    )
    assert response.status_code == 404
    data = response.json()
    assert "Could not find port/region: MYHOUSE" in data["detail"]


def test_get_rates_wrong_destination(client):
    response = client.get(
        "/rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=santa_pola"
    )
    assert response.status_code == 404
    data = response.json()
    assert "Could not find port/region: santa_pola" in data["detail"]
