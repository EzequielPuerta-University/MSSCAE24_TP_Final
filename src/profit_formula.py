class ProfitFormula:
    def __init__(
        self,
        price: float,
        fixed_cost: float,
        marginal_cost: float,
        profit_period: int,
        delta_price: float = 0.02,
        max_price: float = 200,
    ) -> None:
        self.price = price
        self.fixed_cost = fixed_cost
        self.marginal_cost = marginal_cost
        self.profit_period = profit_period
        self.delta_price = delta_price
        self.last_profit: float = 0
        self.sales_within_period: int = 0
        self.__current_factor: int = 1
        self.__initial_profit_period: int = profit_period
        self.max_price = max_price

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
            self.price = self.compute_new_price()
            self.profit_period = self.__initial_profit_period
            self.sales_within_period = 0
        return period_finished

    def compute_new_price(self) -> float:
        current_profit = self._apply(sales=self.sales_within_period)
        previous_profit = self.last_profit
        self.last_profit = current_profit
        increased = current_profit >= previous_profit
        if self.sales_within_period == 0:
            self.__current_factor = -1
        elif not increased:
            self.__current_factor = self.__current_factor * (-1)
        delta = self.delta_price * self.__current_factor
        return self.clamp(self.price * (1+delta))

    def clamp(self, price) -> float:
        return max(0, min(price, self.max_price))

