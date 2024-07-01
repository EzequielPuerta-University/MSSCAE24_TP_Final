from statistics import mean
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
        price_ratio: Tuple[float, float] = (1.1, 2),
        fixed_cost: Tuple[float, float] = (250_000, 10_000),
        marginal_cost: Tuple[float, float] = (30.0, 5.0),
        quantity_to_buy: Tuple[int, int] = (4000, 1500),
        profit_period: int = 5,
        producer_probability: float = 0.1,
        bankrupt_enabled: bool = False,
        *args,
        **kwargs,
    ):
        self.capital = capital
        self.stock = stock
        self.price_ratio = price_ratio
        self.fixed_cost = fixed_cost
        self.marginal_cost = marginal_cost
        self.quantity_to_buy = quantity_to_buy
        self.profit_period = profit_period
        self.producer_probability = producer_probability
        self.bankrupt_enabled = bankrupt_enabled

        length = kwargs.get("length")
        configuration = kwargs.pop(
            "configuration",
            Lattice.with_probability(
                self.producer_probability,
                cast(int, length),
            ),
        )

        kwargs["configuration"] = configuration

        super(Market, self).__init__(
            *args,
            update_simultaneously=True,
            update_sorted_by_agent_type=True,
            **kwargs,
        )

    def _create_agent(self, basic_agent: Agent, i: int, j: int) -> Agent:
        if basic_agent.agent_type == Consumer.TYPE:
            agent = Consumer()
        elif basic_agent.agent_type == Producer.TYPE:
            marginal_cost = abs(np.random.normal(*self.marginal_cost))
            price_ratio = np.random.uniform(*self.price_ratio)
            agent = Producer(
                capital=self.capital,
                stock=self.stock,
                price=marginal_cost * price_ratio,
                fixed_cost=abs(np.random.normal(*self.fixed_cost)),
                marginal_cost=marginal_cost,
                profit_period=self.profit_period,
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
                if self.bankrupt_enabled and agent.bankrupted:
                    pass
                else:
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
            if sellers:
                agent.buy(amount=np.random.normal(*self.quantity_to_buy), sellers=sellers)
            else:
                # Consumer has no Producers in it's neighborhood.
                pass
        elif _type == Producer.TYPE:
            if self.bankrupt_enabled and agent.bankrupted:
                pass
            else:
                agent.balance_check()
        else:
            raise ValueError(f"Unexpected agent type {_type} at ({i}, {j})")

    # Funciones auxiliares para las series
    def __is_bankrupted(self, producer: Producer) -> bool:
        return self.bankrupt_enabled and producer.bankrupted

    def __get_last_profit(self, i: int, j: int) -> float:
        agent = self.get_agent(i, j)
        if agent.agent_type == Producer.TYPE:
            return np.nan if self.__is_bankrupted(agent) else agent.last_profit
        else:
            return np.nan

    def __get_percent_profit_change(self, i: int, j: int) -> float:
        agent = self.get_agent(i, j)
        if agent.agent_type == Producer.TYPE:
            if self.__is_bankrupted(agent):
                return np.nan
            return (
                (agent.last_profit - agent.previous_profit) / agent.previous_profit * 100
                if agent.previous_profit != 0
                else 0
            )
        else:
            return np.nan

    def __get_percent_price_change(self, i: int, j: int) -> float:
        agent = self.get_agent(i, j)
        if agent.agent_type == Producer.TYPE:
            if self.__is_bankrupted(agent):
                return np.nan
            return (
                (agent.price - agent.previous_price) / agent.previous_price * 100
                if agent.previous_price != 0
                else 0
            )
        else:
            return np.nan

    def __get_capital(self, i: int, j: int) -> float:
        agent = self.get_agent(i, j)
        if agent.agent_type == Producer.TYPE:
            return np.nan if self.__is_bankrupted(agent) else agent.capital
        else:
            return np.nan

    def __get_price(self, i: int, j: int) -> float:
        agent = self.get_agent(i, j)
        if agent.agent_type == Producer.TYPE and self.__is_bankrupted(agent):
            return np.nan
        return agent.price

    def __collect(self, agent_type: int) -> Callable:  # type: ignore[type-arg]
        def _collector(i: int, j: int) -> float | None:
            agent = self.get_agent(i, j)
            if agent.agent_type == agent_type:
                return agent.price
            else:
                return None

        return _collector

    # Series de grilla
    @as_series
    def agent_types_lattice(self) -> List[List[int]]:
        action = lambda i, j: int(self.get_agent(i, j).agent_type)
        return self._process_lattice_with(action)

    @as_series
    def price_lattice(self) -> List[List[float]]:
        action = lambda i, j: self.__get_price(i, j)
        return self._process_lattice_with(action)

    @as_series
    def capital_lattice(self) -> List[List[float]]:
        action = lambda i, j: self.__get_capital(i, j)
        return self._process_lattice_with(action)

    # Series categorizadas
    @as_series
    def agent_types_categorized_lattice(self) -> List[List[Tuple[float, int]]]:
        action = lambda i, j: (
            int(self.get_agent(i, j).agent_type),
            self.get_agent(i, j).agent_type,
        )
        return self._process_lattice_with(action)

    @as_series
    def price_categorized_lattice(self) -> List[List[Tuple[float, int]]]:
        action = lambda i, j: (int(self.get_agent(i, j).price), self.get_agent(i, j).agent_type)
        return self._process_lattice_with(action)

    @as_series
    def profit_categorized_lattice(self) -> List[List[Tuple[float, int]]]:
        action = lambda i, j: (self.__get_last_profit(i, j), self.get_agent(i, j).agent_type)
        return self._process_lattice_with(action)

    @as_series
    def capital_categorized_lattice(self) -> List[List[Tuple[float, int]]]:
        action = lambda i, j: (self.__get_capital(i, j), self.get_agent(i, j).agent_type)
        return self._process_lattice_with(action)

    @as_series
    def percent_profit_change_lattice(self) -> List[List[Tuple[float, int]]]:
        action = lambda i, j: (
            self.__get_percent_profit_change(i, j),
            self.get_agent(i, j).agent_type,
        )
        return self._process_lattice_with(action)

    @as_series
    def percent_price_change_lattice(self) -> List[List[Tuple[float, int]]]:
        action = lambda i, j: (
            self.__get_percent_price_change(i, j),
            self.get_agent(i, j).agent_type,
        )
        return self._process_lattice_with(action)

    # Series numericas
    @as_series
    def average_profit(self) -> float:
        action = lambda i, j: self.__get_last_profit(i, j)
        profits = self._process_lattice_with(action, flatten=True)
        profits = filter(lambda profit: not np.isnan(profit), profits)
        return mean(profits)

    @as_series_with(depends=("percent_profit_change_lattice",))
    def average_profit_change(self) -> float:
        changes = self._flatten("percent_profit_change_lattice")
        changes = filter(
            lambda change: not np.isnan(change), map(lambda change: change[0], changes)
        )
        return mean(changes)

    @as_series_with(depends=("price_lattice",))
    def average_price(self) -> float:
        prices = self._flatten("price_lattice")
        return sum(prices) / self.length**2

    @as_series_with(depends=("percent_price_change_lattice",))
    def average_price_change(self) -> float:
        changes = self._flatten("percent_price_change_lattice")
        changes = filter(
            lambda change: not np.isnan(change), map(lambda change: change[0], changes)
        )
        return mean(changes)

    @as_series
    def average_consumer_price(self) -> float:
        prices = self._process_lattice_with(
            self.__collect(Consumer.TYPE),
            flatten=True,
        )
        prices = filter(lambda price: price is not None, prices)
        return mean(prices)

    @as_series
    def average_producer_price(self) -> float:
        prices = self._process_lattice_with(
            self.__collect(Producer.TYPE),
            flatten=True,
        )
        prices = filter(lambda price: price is not None, prices)
        return mean(prices)

    @as_series
    def gini_prices_distribution(self) -> float:
        prices = self._process_lattice_with(
            self.__collect(Consumer.TYPE),
            flatten=True,
        )
        prices = [int(p) for p in filter(lambda price: price is not None, prices)]
        mad = np.abs(np.subtract.outer(prices, prices)).mean()
        mean = np.nanmean(prices)
        # Relative mean absolute difference
        rmad = mad / mean if mean else 0
        # Gini coefficient
        return 0.5 * rmad

    @as_series
    def alive_producers(self) -> float:
        count = 0.0

        def count_alive_producers(i: int, j: int) -> None:
            nonlocal count
            agent = self.get_agent(i, j)
            if agent.agent_type == Producer.TYPE and not self.__is_bankrupted(agent):
                count += 1

        self._process_lattice_with(lambda i, j: count_alive_producers(i, j))
        return count
