from typing import Any, Dict, List

import numpy as np
from simulab.simulation.core.equilibrium_criterion import WithoutCriterion
from simulab.simulation.core.experiment import ExperimentParametersSet
from simulab.simulation.core.lattice import Lattice
from simulab.simulation.core.neighborhood import ExpandedMoore
from simulab.simulation.core.runner import Runner

from src.consumer import Consumer
from src.market import Market
from src.producer import Producer

length = 20
capital = 1_000
stock = 5_000_000_000
producer_probability = 0.25
profit_period = 7
price_ratio = (1.2, 1.5)
fixed_cost = (10, 1)
marginal_cost = (10, 1)
quantity_to_buy = (1, 0)
criterion = WithoutCriterion()


def create_configuration(producer_probability: float = producer_probability) -> Lattice:
    configuration = Lattice.with_probability(producer_probability, length)

    for i in range(length):
        for j in range(length):
            agent_type = configuration.at(i, j)
            if agent_type == Consumer.TYPE:
                agent = Consumer()
            else:
                _marginal_cost = abs(np.random.normal(*marginal_cost))
                _price_ratio = np.random.uniform(*price_ratio)
                agent = Producer(
                    capital=capital,
                    stock=stock,
                    price=_marginal_cost * _price_ratio,
                    fixed_cost=abs(np.random.normal(*fixed_cost)),
                    marginal_cost=_marginal_cost,
                    profit_period=profit_period,
                )
            configuration.set(i, j, _with=agent)
    return configuration


def parameters_with(
    configuration: Lattice, bankrupt_enabled: bool = False
) -> ExperimentParametersSet:
    return ExperimentParametersSet(
        length=[length],
        neighborhood=[ExpandedMoore(3)],
        agent_types=[2],
        capital=[capital],
        producer_probability=[producer_probability],
        profit_period=[profit_period],
        price_ratio=[price_ratio],
        fixed_cost=[fixed_cost],
        marginal_cost=[marginal_cost],
        quantity_to_buy=[quantity_to_buy],
        bankrupt_enabled=[bankrupt_enabled],
        configuration=[configuration],
    )


def bankrupted_on(runner: Runner) -> List[bool]:
    producer_positions = set(runner.experiments[0]._by_type[1])
    return [
        runner.experiments[0].configuration.at(*position).capital <= 0
        for position in producer_positions
    ]


def execute_with(
    configuration: Lattice,
    data: Dict[str, List[Any]],
    strategy_name: str,
    max_steps: int = 1000,
    bankrupt_enabled: bool = False,
) -> None:
    params = parameters_with(configuration, bankrupt_enabled=bankrupt_enabled)
    runner = Runner(Market, params, criterion, max_steps=max_steps)
    runner.start()
    producer_positions = set(runner.experiments[0]._by_type[1])
    producers_amount = len(producer_positions)
    current_bankrupted = bankrupted_on(runner).count(True)
    data["Capital"] = data["Capital"] + ["sin capital", "con capital"]
    data["Cantidad"] = data["Cantidad"] + [
        current_bankrupted,
        producers_amount - current_bankrupted,
    ]
    data["Estrategia"] = data["Estrategia"] + ([strategy_name] * 2)
