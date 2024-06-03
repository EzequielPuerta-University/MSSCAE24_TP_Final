from typing import Callable

import pytest

from src.producer import Producer


@pytest.fixture
def initial_capital() -> float:  # type: ignore[misc]
    yield 1_000_000


@pytest.fixture
def producer(initial_capital) -> Callable:  # type: ignore
    def __producer(
        stock: int = 200_000,
        price: float = 10.0,
        fixed_cost: float = 500_000.0,
        marginal_cost: float = 3.5,
        profit_period: int = 10,
    ) -> Producer:
        return Producer(
            capital=initial_capital,
            stock=stock,
            price=price,
            fixed_cost=fixed_cost,
            marginal_cost=marginal_cost,
            profit_period=profit_period,
        )

    yield __producer


def test_producer_creation(  # type: ignore[no-untyped-def]
    producer,
    initial_capital,
) -> None:
    producer = producer()
    assert producer.capital == initial_capital
    assert producer.stock == 200_000
    assert producer.price == 10.0
    assert producer.TYPE == 1
    assert producer.agent_type == producer.TYPE
    assert producer.profit_formula.price == 10.0
    assert producer.profit_formula.fixed_cost == 500_000.0
    assert producer.profit_formula.marginal_cost == 3.5
    assert producer.profit_formula.profit_period == 10


def test_producer_sales(  # type: ignore[no-untyped-def]
    producer,
) -> None:
    producer = producer()
    assert producer.stock == 200_000
    assert producer.capital == 1_000_000
    producer.sale(50_000)
    assert producer.stock == 150_000
    assert producer.capital == 1_000_000


def test_producer_can_do_many_sales_per_iteration(  # type: ignore[no-untyped-def]
    producer,
) -> None:
    producer = producer()
    assert producer.stock == 200_000
    assert producer.capital == 1_000_000
    producer.sale(50_000)
    assert producer.stock == 150_000
    assert producer.capital == 1_000_000
    producer.sale(100_000)
    assert producer.stock == 50_000
    assert producer.capital == 1_000_000


def test_producer_with_insufficient_stock(  # type: ignore[no-untyped-def]
    producer,
) -> None:
    producer = producer()
    assert producer.stock == 200_000
    assert producer.capital == 1_000_000
    producer.sale(100_000)
    assert producer.stock == 100_000
    assert producer.capital == 1_000_000
    with pytest.raises(AssertionError) as error:
        producer.sale(amount=150_000)
    assert error.value.args[0] == "Insufficient stock"
    assert producer.stock == 100_000
    assert producer.capital == 1_000_000


def test_producer_increases_the_price(  # type: ignore[no-untyped-def]
    producer,
) -> None:
    days = 3
    producer = producer(profit_period=days)
    initial_capital = producer.capital
    initial_stock = producer.stock

    sales_per_day = {
        1: [30_000],
        2: [10_000, 20_000],
        3: [10_000, 10_000, 10_000],
    }
    sales_amount = sum(sum(sales_per_day.values(), []))

    assert sales_amount == 90_000
    for sales in sales_per_day.values():
        for amount in sales:
            producer.sale(amount=amount)
        assert producer.price == 10.0
        assert producer.capital == initial_capital
        producer.balance_check()
    assert producer.price == 10.1
    assert producer.capital == initial_capital + 85_000
    assert producer.stock == initial_stock - sales_amount


def test_producer_decreases_the_price(  # type: ignore[no-untyped-def]
    producer,
) -> None:
    days = 3
    producer = producer(profit_period=days)
    initial_capital = producer.capital
    initial_stock = producer.stock

    sales_per_day = {
        1: [25_000],
        2: [20_000, 10_000],
        3: [5_000, 5_000, 5_000],
    }
    sales_amount = sum(sum(sales_per_day.values(), []))

    assert sales_amount == 70_000
    for sales in sales_per_day.values():
        for amount in sales:
            producer.sale(amount=amount)
        assert producer.price == 10.0
        assert producer.capital == initial_capital
        producer.balance_check()
    assert producer.price == 9.9
    assert producer.capital == initial_capital - 45_000.0
    assert producer.stock == initial_stock - sales_amount


def test_producer_can_increase_the_price_many_times(  # type: ignore[no-untyped-def]
    producer,
) -> None:
    days = 3
    producer = producer(profit_period=days)
    initial_capital = producer.capital
    initial_stock = producer.stock

    sales_per_day = {
        1: [30_000],
        2: [10_000, 20_000],
        3: [10_000, 10_000, 10_000],
    }
    sales_amount = sum(sum(sales_per_day.values(), []))

    expected_values = {
        0: {
            "price": 10.1,
            "capital": initial_capital + 85_000,
            "stock": initial_stock - sales_amount,
        },
        1: {
            "price": 10.201,
            "capital": initial_capital + 85_000 + 94_000,
            "stock": initial_stock - (sales_amount * 2),
        },
    }
    assert sales_amount == 90_000
    for i in range(2):
        for sales in sales_per_day.values():
            for amount in sales:
                producer.sale(amount=amount)
            producer.balance_check()
        assert producer.price == expected_values[i]["price"]
        assert producer.capital == expected_values[i]["capital"]
        assert producer.stock == expected_values[i]["stock"]


# def test_producer_can_decrease_the_price_many_times(  # type: ignore[no-untyped-def]
#     producer,
# ) -> None:
#     days = 3
#     producer = producer(profit_period=days)
#     initial_capital = producer.capital
#     initial_stock = producer.stock

#     first_sales = {
#         1: [25_000],
#         2: [20_000, 10_000],
#         3: [5_000, 5_000, 5_000],
#     }
#     first_sales_amount = sum(sum(first_sales.values(), []))
#     assert first_sales_amount == 70_000
#     for sales in first_sales.values():
#         for amount in sales:
#             producer.sale(amount=amount)
#         producer.balance_check()
#     assert producer.price == 9.9
#     assert producer.capital == initial_capital - 45_000.0
#     assert producer.stock == initial_stock - first_sales_amount

#     last_sales = {
#         1: [5_000],
#         2: [5_000, 5_000],
#         3: [5_000, 5_000, 5_000],
#     }
#     last_sales_amount = sum(sum(last_sales.values(), []))
#     assert last_sales_amount == 30_000
#     for sales in last_sales.values():
#         for amount in sales:
#             producer.sale(amount=amount)
#         producer.balance_check()
#     assert producer.price == 9.801
#     assert producer.capital == initial_capital - 45_000.0 - 52_000.0
#     assert producer.stock == initial_stock - first_sales_amount - last_sales_amount


# def test_producer_changes_its_price_(  # type: ignore[no-untyped-def]
#     producer,
# ) -> None:
#     days = 3
#     producer = producer(profit_period=days)
#     initial_capital = producer.capital
#     initial_stock = producer.stock

#     sales_per_day = {
#         1: [30_000],
#         2: [10_000, 20_000],
#         3: [10_000, 10_000, 10_000],
#     }
#     sales_amount = sum(sum(sales_per_day.values(), []))

#     expected_values = {
#         0: {
#             "price": 10.1,
#             "capital": initial_capital + 85_000,
#             "stock": initial_stock - sales_amount,
#             },
#         1: {
#             "price": 10.201,
#             "capital": initial_capital + 85_000 + 94_000,
#             "stock": initial_stock - (sales_amount * 2),
#             },
#     }
#     assert sales_amount == 90_000
#     for i in range(2):
#         for sales in sales_per_day.values():
#             for amount in sales:
#                 producer.sale(amount=amount)
#             producer.balance_check()
#         assert producer.price == expected_values[i]["price"]
#         assert producer.capital == expected_values[i]["capital"]
#         assert producer.stock == expected_values[i]["stock"]
