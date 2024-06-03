from typing import List

from simulab.models.abstract.agent import Agent

from src.producer import Producer


class Consumer(Agent):
    TYPE = 0

    def __init__(self) -> None:
        self.price: float = 0
        super(Consumer, self).__init__(self.TYPE)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(price={self.price})"

    def buy(self, amount: int, sellers: List[Producer]) -> None:
        cheapest = sellers[0]
        for seller in sellers[1:]:
            if seller.price < cheapest.price:
                cheapest = seller
        cheapest.sale(amount)
        self.price = cheapest.price
