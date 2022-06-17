
def test_instant_effect(test_actor, test_damage_effect):
    test_damage_effect.apply(target=test_actor)
    assert test_actor.hp.value == 5
