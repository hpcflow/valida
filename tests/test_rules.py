import pytest
from valida.errors import MalformedRuleSpec

from valida.rules import Rule
from valida.casting import cast_string_to_bool
from valida.conditions import Key, Value
from valida.data import Data
from valida.datapath import DataPath, MapValue


# assert rule from spec check
def test_equivalence_of_Rule_from_spec():
    assert Rule.from_spec(
        {
            "path": ["A", "B", "C"],
            "condition": {"value.dtype.eq": int},
        }
    ) == Rule(["A", "B", "C"], Value.dtype.eq(int))


def test_equivalence_Rule_test_concrete_DataPath_with_without():
    data = Data({"a": [1, 2, 3], "b": 2})
    condition = Value.dtype.equal_to(int)

    path_concrete_1 = "b"
    path_concrete_2 = DataPath(path_concrete_1)

    print(f"data: {data}")
    r1 = Rule(path_concrete_1, condition).test(data)
    print(f"data: {data}")
    r2 = Rule(path_concrete_2, condition).test(data)

    assert r1 == r2


def test_rule_test_dict_value_with_Data():
    data = Data({"A": 1})
    path = DataPath("A")
    rule = Rule(path=path, condition=Value.eq(1))
    assert rule.test(data).is_valid


def test_rule_test_dict_value_without_Data():
    data = {"A": 1}
    path = DataPath("A")
    rule = Rule(path=path, condition=Value.eq(1))
    assert rule.test(data).is_valid


def test_rule_test_nested_list_value():
    data = {"A": [0, 1, 2]}
    path = DataPath("A", 1)
    rule = Rule(path=path, condition=Value.eq(1))
    assert rule.test(data).is_valid


def test_rule_test_value_length_equal_to():
    data = {"A": [0, 1, 2]}
    path = DataPath("A")
    rule = Rule(path=path, condition=Value.length.eq(3))
    assert rule.test(data).is_valid


def test_rule_test_value_dtype_equal_to_dict():
    data = {"A": {"b": 1, "c": 2}}
    path = DataPath("A")
    rule = Rule(path=path, condition=Value.dtype.eq(dict))
    assert rule.test(data).is_valid


def test_rule_test_dict_value_keys_equal_to():
    data = {"A": {"b": 1, "c": 2}}
    path = DataPath("A")
    rule = Rule(path=path, condition=Value.keys_equal_to("b", "c"))
    assert rule.test(data).is_valid


def test_rule_test_dict_value_items_contain():
    data = {"A": {"b": 1, "c": 2}}
    path = DataPath("A")
    rule = Rule(path=path, condition=Value.items_contain(b=1))
    assert rule.test(data).is_valid


def test_rule_test_dict_value_items_contain_false():
    data = {"A": {"b": 1, "c": 2}}
    path = DataPath("A")
    rule = Rule(path=path, condition=Value.items_contain(a=1))
    assert not rule.test(data).is_valid


def test_rule_test_keys_is_instance_subpath():
    data = {"A": {"b": 0, "c": 1}, "B": {1: 0}}
    path = DataPath("A")
    rule = Rule(path=path, condition=Value.keys_is_instance(str))
    assert rule.test(data).is_valid


def test_rule_test_keys_is_instance_subpath_false():
    data = {"A": {"b": 0, "c": 1}, "B": {1: 0}}
    path = DataPath("A")
    rule = Rule(path=path, condition=Value.keys_is_instance(int))
    assert not rule.test(data).is_valid


def test_rule_test_keys_is_instance_subpath_non_concrete_subpath():
    data = {"A": {"b": 0, "c": 1}, "B": {"b": 0}, "C": {1: 0}}
    path = DataPath(MapValue(key=Key.in_(["A", "B"])))
    rule = Rule(path=path, condition=Value.keys_is_instance(str))
    assert rule.test(data).is_valid


def test_rule_test_keys_is_instance_subpath_non_concrete_subpath_false():
    data = {"A": {"b": 0, "c": 1}, "B": {"b": 0}, "C": {1: 0}}
    path = DataPath(MapValue(key=Key.in_(["A", "C"])))
    rule = Rule(path=path, condition=Value.keys_is_instance(str))
    assert not rule.test(data).is_valid


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


def test_from_spec_cast_str_to_bool():
    rule_spec = {
        "path": ["telemetry"],
        "cast": {"str": "bool"},
        "condition": {"value.dtype.equal_to": "bool"},
    }
    r1 = Rule.from_spec(rule_spec)
    r2 = Rule(
        path=["telemetry"],
        cast={str: cast_string_to_bool},
        condition=Value.dtype.equal_to(bool),
    )
    assert r1 == r2


def test_from_spec_cast_bad_cast_from_type():
    rule_spec = {
        "path": ["telemetry"],
        "cast": {"bad_type": bool},
        "condition": {"value.dtype.equal_to": "bool"},
    }
    with pytest.raises(MalformedRuleSpec):
        Rule.from_spec(rule_spec)


def test_from_spec_cast_bad_cast_to_type():
    rule_spec = {
        "path": ["telemetry"],
        "cast": {str: "bad_type"},
        "condition": {"value.dtype.equal_to": "bool"},
    }
    with pytest.raises(MalformedRuleSpec):
        Rule.from_spec(rule_spec)


def test_cast_str_to_bool():
    r = Rule(
        path=["telemetry"],
        condition=Value.dtype.equal_to(bool),
        cast={str: cast_string_to_bool},
    )
    data = {"telemetry": "true"}
    rt = r.test(data)
    assert rt.is_valid


def test_no_cast_str_to_bool():
    r = Rule(
        path=[MapValue()],
        condition=Value.dtype.equal_to(bool),
        cast={str: cast_string_to_bool},
    )
    data = {"A": "true", "B": "false", "C": "none"}
    cast_data = Data({"A": True, "B": False, "C": "none"})
    rt = r.test(data)
    assert rt.data == cast_data and rt.num_failures == 1
