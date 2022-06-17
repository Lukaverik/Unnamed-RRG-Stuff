import pytest

from objects.models import Actor, Statistic, HP, Effect
from objects.definitions.enums import DamageTypeEnum, DamageElementEnum

test_stats = {
    "Attack": Statistic(value=5),
    "Defense": Statistic(value=5),
    "Magic": Statistic(value=5),
    "Resistance": Statistic(value=5),
    "Dexterity": Statistic(value=5),
    "Agility": Statistic(value=5),
    "Luck": Statistic(value=5),
    "Hype": Statistic(value=5)
}

@pytest.fixture
def test_actor():
    return Actor(
        name="test_actor",
        hp=HP(value=10),
        stats=test_stats,
        level=1
    )

@pytest.fixture
def test_damage_effect(test_actor):
    def does_5_damage(source: Actor, target: Actor):
        target.damage(5, DamageTypeEnum.Physical, DamageElementEnum.Neutral)
    return Effect(source=test_actor, effect=does_5_damage)