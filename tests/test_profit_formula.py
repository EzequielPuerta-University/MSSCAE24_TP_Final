from typing import Callable

import pytest

from src.profit_formula import ProfitFormula


@pytest.fixture
def profit_formula() -> Callable:  # type: ignore
    def __profit_formula(
        price: float = 10.0,
        fixed_cost: float = 500_000.0,
        marginal_cost: float = 3.5,
        profit_period: int = 1,
    ) -> ProfitFormula:
        return ProfitFormula(
            price=price,
            fixed_cost=fixed_cost,
            marginal_cost=marginal_cost,
            profit_period=profit_period,
        )

    yield __profit_formula


def test_profit_formula_creation(profit_formula) -> None:
    formula = profit_formula(
        price=10.0,
        fixed_cost=500_000.0,
        marginal_cost=3.5,
        profit_period=1,
    )
    assert formula.price == 10.0
    assert formula.fixed_cost == 500_000.0
    assert formula.marginal_cost == 3.5
    assert formula.profit_period == 1
    assert formula.last_profit == 0
    assert formula.sales_within_period == 0


def test_profit_formula_applied(profit_formula) -> None:
    price = 10.0
    fixed_cost = 1_000.0
    marginal_cost = 5
    formula = profit_formula(
        price=price,
        fixed_cost=fixed_cost,
        marginal_cost=marginal_cost,
    )

    sales_amount = 10_000
    profit = formula._apply(sales=sales_amount)
    assert profit == ((price - marginal_cost) * sales_amount - fixed_cost)


# def test_profit_was_increased(profit_formula) -> None:
#     formula = profit_formula()
#     sales_amount = 90_000
#     expected_profit = 85_000.0

#     assert formula.price == 10.0
#     assert formula.last_profit == 0
#     assert expected_profit > formula.last_profit
#     assert formula._apply(sales=sales_amount) == expected_profit
#     assert formula.check(sales=sales_amount)
#     assert formula.price == 10.0 * (1 + formula.delta_price)
#     assert formula.last_profit == expected_profit


# def test_profit_was_decreased(profit_formula) -> None:
#     formula = profit_formula()
#     sales_amount = 70_000
#     expected_profit = -45_000.0

#     assert formula.price == 10.0
#     assert formula.last_profit == 0
#     assert expected_profit < formula.last_profit
#     assert formula._apply(sales=sales_amount) == expected_profit
#     assert formula.check(sales=sales_amount)
#     assert formula.price == 10.0 * (1 - formula.delta_price)
#     assert formula.last_profit == expected_profit


# def test_formula_should_store_all_sales_within_profit_period(
#     profit_formula,
# ) -> None:
#     formula = profit_formula(profit_period=10)
#     sales_amounts = [10_000, 10_000, 10_000, 10_000, 10_000, 10_000, 10_000, 10_000, 5_000, 5_000]
#     accumulated_sales = 0
#     expected_profit = 85_000.0

#     assert formula.profit_period == 10
#     assert formula.sales_within_period == 0
#     assert expected_profit > formula.last_profit

#     for index, sales_amount in enumerate(sales_amounts, start=1):
#         assert formula.profit_period > 0
#         assert formula.price == 10.0
#         assert formula.last_profit == 0
#         assert formula.sales_within_period == accumulated_sales
#         period_finished = formula.check(sales=sales_amount)
#         if index == 10:
#             assert period_finished
#         else:
#             assert not period_finished
#         accumulated_sales = accumulated_sales + sales_amount

#     assert formula.profit_period == 10
#     assert formula.sales_within_period == 0
#     assert formula.price == 10.0 * (1 + formula.delta_price)
#     assert formula.last_profit == expected_profit
