from enum import Enum


# The possible tension levels an actor can have
class TensionEnum(Enum):
    Min = 0
    Low = 1
    Medium = 2
    High = 3
    Max = 4


# The possible types damage can be in the form of
class DamageTypeEnum(Enum):
    Physical = 1
    Arcane = 2
    Pure = 3


# The possible elements damage can have the aspect of
class DamageElementEnum(Enum):
    Neutral = 1
    Fire = 2
    Water = 3
    Air = 4
    Earth = 5
    Electric = 6
    Poison = 7
    Psychic = 8
    Ice = 9
    Dark = 10
    Light = 11
