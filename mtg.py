from mtgsdk import Card
import random


def get_k_cards(k: int):
    return random.choices(
        Card.where(rarity="mythic").where(set="GRN,RNA,WAR").array(), k=k
    )
