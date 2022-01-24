import pytest

from valida.rules import Rule
from valida.conditions import Value
from valida.data import Data
from valida.datapath import DataPath, MapValue

# assert rule from spec check
def test_equivalence_of_Rule_from_spec():
    assert (
        Rule.from_spec(
            {
                "path": ["A", "B", "C"],
                "condition": {"value.dtype.eq": int},
            }
        )
        == Rule(["A", "B", "C"], Value.dtype.eq(int))
    )


def test_equivalence_Rule_test_concrete_DataPath_with_without():

    data = Data({"a": [1, 2, 3], "b": 2})
    condition = Value.dtype.equal_to(int)

    path_concrete_1 = "b"
    path_concrete_2 = DataPath(path_concrete_1)

    r1 = Rule(path_concrete_1, condition).test(data)
    r2 = Rule(path_concrete_2, condition).test(data)

    assert r1 == r2


def test_expected_validity_Rule_test_non_existent_non_concrete_path():
    data = Data({"A": 1})
    path = DataPath(MapValue("B"))
    rule = Rule(path=path, condition=Value.eq(2))
    assert rule.test(data).is_valid


def test_expected_validity_Rule_test_non_existent_concrete_path():
    data = Data({"A": 1})
    path = DataPath("B")
    rule = Rule(path=path, condition=Value.eq(2))
    assert rule.test(data).is_valid
