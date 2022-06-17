import pytest

from objects.models import Model

@pytest.fixture
def model():
    return Model(
        internal_name="test_model",
        test_field="test_field_value"
    )


def test_model_fields(model):
    attributes_set = set(dir(model))
    test_set = {
        "internal_name",
        "test_field",
    }
    assert test_set.issubset(attributes_set)
