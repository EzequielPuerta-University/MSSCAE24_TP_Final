from simulab.models.abstract.agent import Agent

from src.profit_formula import ProfitFormula


class Producer(Agent):
    TYPE = 1

    def __init__(
        self,
        capital: float,
        stock: int,
        price: float,
        fixed_cost: float,
        marginal_cost: float,
        profit_period: int,
        max_price: float,
    ) -> None:
        self.capital = capital
        self.stock = stock
        self.profit_formula = ProfitFormula(
            price=price,
            fixed_cost=fixed_cost,
            marginal_cost=marginal_cost,
            profit_period=profit_period,
            max_price=max_price
        )
        self.__sales_of_the_day = 0
        super(Producer, self).__init__(self.TYPE)

    def __repr__(self) -> str:
        return "{}(capital={}, stock={}, price={})".format(
            type(self).__name__,
            self.capital,
            self.stock,
            self.price,
        )

    @property
    def price(self) -> float:
        return self.profit_formula.price

    def sale(self, amount: int) -> None:
        if self.stock >= amount:
            self.stock = self.stock - amount
            self.__sales_of_the_day = self.__sales_of_the_day + amount
        else:
            raise AssertionError("Insufficient stock")

    def balance_check(self) -> None:
        period_finished = self.profit_formula.check(self.__sales_of_the_day)
        if period_finished:
            self.capital = self.capital + self.profit_formula.last_profit
        self.__sales_of_the_day = 0
