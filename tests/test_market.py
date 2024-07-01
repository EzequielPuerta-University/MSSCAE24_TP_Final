# import pytest
from simulab.simulation.core.equilibrium_criterion import WithoutCriterion
from simulab.simulation.core.experiment import ExperimentParametersSet
from simulab.simulation.core.neighborhood import ExpandedMoore
from simulab.simulation.core.runner import Runner

from src.market import Market

experiment_parameters_set = ExperimentParametersSet(
    length=[50],
    neighborhood=[ExpandedMoore(3)],
    agent_types=[2],
    producer_probability=[0.65],
)
runner = Runner(
    Market,
    experiment_parameters_set,
    WithoutCriterion(),
    max_steps=5,
)


# def test_market() -> None:
#     assert len(runner.experiments) == 1
#     with pytest.raises(AttributeError):
#         runner.experiments[0].series

#     runner.start()
#     for series in runner.experiments[0].series.values():
#         assert len(series) == 5 + 1
