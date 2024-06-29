import random


class ProfitFormula:
    def __init__(
        self,
        price: float,
        fixed_cost: float,
        marginal_cost: float,
        profit_period: int,
        delta_price: float = 0.02,
    ) -> None:
        self.price = price
        self.previous_price = price
        self.fixed_cost = fixed_cost
        self.marginal_cost = marginal_cost
        self.profit_period = profit_period
        self.delta_price = delta_price
        self.previous_profit: float = 0
        self.last_profit: float = 0
        self.sales_within_period: int = 0
        self.__current_factor: int = random.randint(0, 1) * 2 - 1
        self.__initial_profit_period: int = profit_period

    def __repr__(self) -> str:
        txt = "{} (price={}, fixed_cost={}, marginal_cost={}, profit_period={})"
        return txt.format(
            type(self).__name__,
            self.price,
            self.fixed_cost,
            self.marginal_cost,
            self.profit_period,
        )

    def _apply(self, sales: int) -> float:
        return (self.price - self.marginal_cost) * sales - self.fixed_cost

    def check(self, sales: int) -> bool:
        self.profit_period = self.profit_period - 1
        self.sales_within_period = self.sales_within_period + sales

        period_finished = self.profit_period <= 0
        if period_finished:
            self.previous_price = self.price
            self.price = self.__compute_new_price()
            self.profit_period = self.__initial_profit_period
            self.sales_within_period = 0
        return period_finished

    def __compute_new_price(self) -> float:
        current_profit = self._apply(sales=self.sales_within_period)
        self.previous_profit = self.last_profit
        self.last_profit = current_profit
        increased = current_profit >= self.previous_profit

        if self.sales_within_period == 0:
            self.__current_factor = -1
        elif not increased:
            self.__current_factor = self.__current_factor * (-1)

        delta = self.delta_price * self.__current_factor
        return max(self.marginal_cost, self.price * (1 + delta))
