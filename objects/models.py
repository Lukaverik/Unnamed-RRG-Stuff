from typing import Dict, List, Callable

from objects.definitions.enums import TensionEnum, DamageTypeEnum, DamageElementEnum


# Sets up standardized constructors to be used in each object.
class Model:
    def __init__(self, *args, **kwargs):
        for field_name, field_value in kwargs.items():
            setattr(self, f"{field_name}", field_value)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""                                                                                 """
"""                                                                                 """
"                                  Statistics                                         "
"""                                                                                 """
"""                                                                                 """
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


# Statistics are numerical values that define traits of an actor--HP, Attack. Defense, etc
class Statistic(Model):
    # The base value of the Statistic before any modifiers are applied
    # Should only ever be written to on actor creation and on player level up.
    # In every other instance, read only
    base_value: int
    # The actual value of the Statistic after modifiers are applied
    value: int

    def __init__(self, value):
        super().__init__(base_value=value, value=value)

    def __add__(self, value) -> 'Statistic':
        return Statistic(value=self.value + value)

    def __sub__(self, value) -> 'Statistic':
        return Statistic(value=self.value - value)

    def reset(self) -> None:
        self.value = self.base_value


# HP is just a Statistic that has a bit more validation on it (can't be healed above max or brought below 0, etc.)
class HP(Statistic):
    def __add__(self, value) -> 'HP':
        return HP(value=min(self.value + value, self.base_value))

    def __sub__(self, value) -> 'HP':
        return HP(value=max(self.value - value, 0))


"""
Default Statistics
HP - The amount of damage an Actor can sustain before falling in combat
Attack - An Actor's physical offensive capability
Defense - An Actor's physical defensive capability
Magic - An Actor's arcane offensive capability
Resistance - An Actor's arcane defensive capability
Dexterity - An Actor's offensive speed -- weighed against target Agility to determine hit
Agility - An Actor's defensive speed -- weighed against aggressor Dexterity to determine hit
^^^^^^ The higher value between Dexterity and Agility is used in turn order calculations
Luck - An Actor's critical hit/critical success rate
Hype - The amount of progress towards the next (or previous) Tension level -- reset after combat
"""


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""                                                                                 """
"""                                                                                 """
"                                    Effects                                          "
"""                                                                                 """
"""                                                                                 """
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def default_effect(source: 'Actor', target: 'Actor') -> None:
    pass


class Effect(Model):
    source: 'Actor'
    effect: Callable[['Actor', 'Actor'], None] = default_effect

    def __init__(self, source: 'Actor', effect: Callable[['Actor', 'Actor'], None], **kwargs):
        super().__init__(source=source, effect=effect, **kwargs)

    def apply(self, target: 'Actor'):
        self.effect(source=self.source, target=target)


class LastingEffect(Effect):
    duration: int
    is_multiplicative: bool
    undo_effect: Callable[['Actor', 'Actor'], None] = default_effect

    def __init__(
            self,
            source: 'Actor',
            duration: int,
            is_multiplicative: bool,
            effect: Callable[['Actor', 'Actor'], None],
            undo_effect: Callable[['Actor', 'Actor'], None]
    ):
        super().__init__(
            source=source,
            duration=duration,
            is_multiplicative=is_multiplicative,
            effect=effect,
            undo_effect=undo_effect
        )

    def cleanse(self, target: 'Actor'):
        self.undo_effect(source=self.source, target=target)

# TODO -- Passive Effects? How are they handled? Types: (On-hit, Damage Type Resistance, ...?)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""                                                                                 """
"""                                                                                 """
"                                     Items                                           "
"""                                                                                 """
"""                                                                                 """
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


class Item(Model):
    pass


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""                                                                                 """
"""                                                                                 """
"                                    Actors                                           "
"""                                                                                 """
"""                                                                                 """
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


# Actors are anything that takes a turn in combat--enemy, ally, or player
class Actor(Model):
    # The name of the Actor
    name: str
    # A dictionary mapped from stat name to Statistic
    # The list of standard Statistics and their purposes is listed above
    stats: Dict[str, Statistic] = {}
    # HP is treated differently than rest of stats, separated out from stats dict
    hp: HP
    # The experience level of the actor
    level: int = 1
    # The hype level of the actor
    tension: TensionEnum = TensionEnum.Min
    # The list of lasting effects currently applied to the actor
    lasting_effects: List[LastingEffect] = []
    # # The list of passive effects currently applied to actor
    # passive_effects: List[PassiveEffect]

    def damage(self, damage_amount: int, damage_type: DamageTypeEnum, damage_element: DamageElementEnum) -> None:
        post_mitigation_damage: int = damage_amount

        # TODO Damage Element and/or Damage Type Resistances?

        if damage_type == DamageTypeEnum.Physical:
            post_mitigation_damage *= 100 / (100 + self.stats["Defense"].value)
        elif damage_type == DamageTypeEnum.Arcane:
            post_mitigation_damage *= 100 / (100 + self.stats["Resistance"].value)

        self.hp -= round(post_mitigation_damage)

    def handle_lasting_effects(self) -> None:
        for stat in list(self.stats.values()):
            stat.reset()
        for effect in self.lasting_effects:
            new_duration = effect.duration - 1
            if new_duration == 0:
                self.lasting_effects.remove(effect)
                effect.cleanse(target=self)
            else:
                effect.apply(target=self)
        self.lasting_effects = sorted(self.lasting_effects, key=lambda x: x.is_multiplicative, reverse=True)


class Ally(Actor):
    # The number of total experience points the Ally has accrued
    exp: int


class Enemy(Actor):
    # The ratio applied against the enemy level to calc xp on defeat
    xp_ratio: float
    # The ratio applied against the enemy level to calc tension on defeat
    hype_ratio: float
    loot_table: Dict[float, Item]


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""                                                                                 """
"""                                                                                 """
"                                    Combat                                           "
"""                                                                                 """
"""                                                                                 """
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


class Combat(Model):
    player_team: List[Ally]
    enemy_team: List[Enemy]