from typing import Callable, List, Tuple, cast

import numpy as np
from simulab.models.abstract.agent import Agent
from simulab.models.abstract.model import (
    AbstractLatticeModel,
    as_series,
    as_series_with,
)
from simulab.simulation.core.lattice import Lattice

from src.consumer import Consumer
from src.producer import Producer


class Market(AbstractLatticeModel):
    def __init__(  # type: ignore[no-untyped-def]
        self,
        capital: float = 1_000_000,
        stock: int = 5_000_000_000,
        price: Tuple[float, float] = (1.1, 2),
        fixed_cost: Tuple[float, float] = (250, 30),
        marginal_cost: Tuple[float, float] = (30.0, 5.0),
        quantity_to_buy: Tuple[int, int] = (4000, 1500),
        profit_period: int = 5,
        producer_probability: float = 0.1,
        max_price: float = 200,
        *args,
        **kwargs,
    ):
        self.capital = capital
        self.stock = stock
        self.price = price
        self.fixed_cost = fixed_cost
        self.marginal_cost = marginal_cost
        self.quantity_to_buy = quantity_to_buy
        self.profit_period = profit_period
        self.producer_probability = producer_probability
        self.max_price = max_price

        length = kwargs.get("length")
        configuration = kwargs.get(
            "configuration",
            Lattice.with_probability(
                self.producer_probability,
                cast(int, length),
            ),
        )

        super(Market, self).__init__(
            *args,
            update_simultaneously=True,
            update_sorted_by_agent_type=True,
            configuration=configuration,
            **kwargs,
        )

    def _create_agent(self, basic_agent: Agent, i: int, j: int) -> Agent:
        if basic_agent.agent_type == Consumer.TYPE:
            agent = Consumer()
        elif basic_agent.agent_type == Producer.TYPE:
            marginal_cost = np.random.normal(*self.marginal_cost)
            price_multiplier = np.random.uniform(*self.price)
            agent = Producer(
                capital=self.capital,
                stock=self.stock,
                price=marginal_cost*price_multiplier,
                fixed_cost=np.random.normal(*self.fixed_cost),
                marginal_cost=marginal_cost,
                profit_period=self.profit_period,
                max_price=self.max_price,
            )
        else:
            raise ValueError(
                f"Invalid agent type. Values {Consumer.TYPE} or {Producer.TYPE} expected"
            )
        return agent

    def __sellers_for(
        self,
        i: int,
        j: int,
        configuration: Lattice,
    ) -> List[Producer]:
        neighbors = self.neighborhood.indexes_for(i, j)
        sellers = []
        for position in neighbors:
            agent = configuration.at(*position)
            if agent.agent_type == Producer.TYPE:
                sellers.append(agent)
        return sellers

    def step(
        self,
        i: int,
        j: int,
        configuration: Lattice,
    ) -> None:
        agent = configuration.at(i, j)
        _type = agent.agent_type
        if _type == Consumer.TYPE:
            sellers = self.__sellers_for(i, j, configuration)
            if len(sellers) == 0: return
            agent.buy(
                amount=np.random.normal(*self.quantity_to_buy),
                sellers=sellers,
            )
        elif _type == Producer.TYPE:
            agent.balance_check()
        else:
            raise ValueError(f"Unexpected agent type {_type} at ({i}, {j})")

    @as_series
    def agent_types_lattice(self) -> List[List[int]]:
        action = lambda i, j: int(self.get_agent(i, j).agent_type)
        return self._process_lattice_with(action)

    @as_series
    def price_lattice(self) -> List[List[float]]:
        action = lambda i, j: int(self.get_agent(i, j).price)
        return self._process_lattice_with(action)

    @as_series_with(depends=("price_lattice",))
    def average_price(self) -> float:
        prices = self._flatten("price_lattice")
        return sum(prices) / self.length**2

    def __collect(self, agent_type: int) -> Callable:  # type: ignore[type-arg]
        def _collector(i: int, j: int) -> float | None:
            agent = self.get_agent(i, j)
            if agent.agent_type == agent_type:
                return agent.price
            else:
                return None

        return _collector

    @as_series
    def average_consumer_price(self) -> float:
        prices = self._process_lattice_with(
            self.__collect(Consumer.TYPE),
            flatten=True,
        )
        prices = list(filter(lambda price: price is not None, prices))
        return sum(prices) / len(prices)

    @as_series
    def average_producer_price(self) -> float:
        prices = self._process_lattice_with(
            self.__collect(Producer.TYPE),
            flatten=True,
        )
        prices = list(filter(lambda price: price is not None, prices))
        return sum(prices) / len(prices)

    @as_series
    def profit_lattice(self) -> List[List[float]]:
        return self._process_lattice_with(self.get_last_profit)

    def get_last_profit(self, i, j) -> float:
        try:
            return self.get_agent(i, j).profit_formula.last_profit
        except AttributeError:
            return -1