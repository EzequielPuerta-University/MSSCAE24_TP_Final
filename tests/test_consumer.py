from typing import Callable

import pytest

from src.consumer import Consumer
from src.producer import Producer


@pytest.fixture
def producer() -> Callable:  # type: ignore
    def __producer(
        stock: int = 10,
        price: float = 10.0,
        fixed_cost: float = 500_000.0,
        marginal_cost: float = 3.5,
        profit_period: int = 10,
    ) -> Producer:
        return Producer(
            capital=100,
            stock=stock,
            price=price,
            fixed_cost=fixed_cost,
            marginal_cost=marginal_cost,
            profit_period=profit_period,
        )

    yield __producer


def test_consumer_creation() -> None:
    consumer = Consumer()
    assert consumer.TYPE == 0
    assert consumer.agent_type == consumer.TYPE
    assert consumer.price == 0


def test_consumer_buys_the_cheapest_product(  # type: ignore[no-untyped-def]
    producer,
) -> None:
    capital = 100
    stock = 10
    cheapest = producer(price=1.90)
    not_bad = producer(price=1.95)
    regular = producer(price=2.00)
    expensive = producer(price=2.05)
    not_cheap = [not_bad, expensive, regular]
    sellers = not_cheap + [cheapest]
    for seller in sellers:
        assert seller.capital == capital
        assert seller.stock == stock

    consumer = Consumer()
    assert consumer.price == 0
    amount_to_buy = 1
    consumer.buy(sellers=sellers, amount=amount_to_buy)

    assert consumer.price == cheapest.price
    for seller in not_cheap:
        assert seller.capital == capital
        assert seller.stock == stock
    assert cheapest.stock == stock - amount_to_buy
