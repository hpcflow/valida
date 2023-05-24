import pathlib
import pytest

from valida.conditions import (
    Condition,
    KeyDataType,
    KeyLength,
    ValueDataType,
    ValueLength,
    KeyLike,
    Value,
    Key,
    Index,
    NullCondition,
    ConditionAnd,
    ConditionOr,
    ConditionXor,
    ConditionLike,
)
from valida.datapath import DataPath, ListValue, MapValue
from valida.errors import InvalidCallable, MalformedConditionLikeSpec


def test_mixed_key_index_binary_condition_raises_type_error():
    with pytest.raises(TypeError):
        Key.equal_to(1) | Index.equal_to(1)


def test_mixed_key_index_second_order_binary_condition_raises_type_error():
    with pytest.raises(TypeError):
        vc1 = Value.equal_to(1)
        kc1 = Key.equal_to(1)
        ic1 = Index.equal_to(1)

        mc1 = vc1 | kc1
        mc2 = vc1 | ic1

        mc1 | mc2


def test_null_condition_does_not_generate_binary_condition():
    c1 = Value.equal_to(1)
    assert ConditionAnd(c1, NullCondition()) == c1
    assert ConditionAnd(NullCondition(), c1) == c1
    assert ConditionOr(c1, NullCondition()) == c1
    assert ConditionOr(NullCondition(), c1) == c1
    assert ConditionXor(c1, NullCondition()) == c1
    assert ConditionXor(NullCondition(), c1) == c1


def test_null_condition_filter_includes_all_list_items():
    my_list = [1, 2, 3]
    assert NullCondition().filter(my_list).data == my_list


def test_null_condition_filter_includes_all_map_items():
    my_dict = {"a": 1, "b": 2, "c": 3}
    assert NullCondition().filter(my_dict).data == list(my_dict.values())


def test_condition_callable_aliases():
    assert Value.eq(1) == Value.equal_to(1)
    assert Value.lt(1) == Value.less_than(1)
    assert Value.gt(1) == Value.greater_than(1)
    assert Value.lte(1) == Value.less_than_or_equal_to(1)
    assert Value.gte(1) == Value.greater_than_or_equal_to(1)


def test_removal_of_null_condition_from_binary_ops():
    c1 = Value.gt(5) & NullCondition()
    assert not any(i.is_null for i in c1.flatten()[0])

    c1 = Value.lt(3) | Value.gt(5) & NullCondition()
    assert not any(i.is_null for i in c1.flatten()[0])


def test_equality():
    c1 = Value.truthy()
    c2 = Value.truthy()
    assert c1 == c2

    c1 = Value.gte(3.5)
    c2 = Value.gte(3.5)
    assert c1 == c2

    c1 = Value.equal_to(1.2)
    c2 = Value.equal_to(2.1)
    assert c1 != c2

    c1 = Value.equal_to(1.2)
    c2 = Value.gte(1.2)
    assert c1 != c2

    c1 = Value.length.equal_to(1)
    c2 = Value.length.equal_to(1)
    assert c1 == c2

    c1 = Key.in_([1, 2, 3])
    c2 = Key.in_([1, 2, 3])
    assert c1 == c2


def test_evalable_repr_for_simple_conditions():
    c1 = Value.equal_to(1)
    c2 = Value.lte(2)
    c3 = Value.not_equal_to(1)

    c4 = c1 & c2
    c5 = c2 | c3 & c1

    for i in (c1, c2, c3, c4, c5):
        assert eval(repr(i)) == i


def test_evalable_repr_for_simple_list_value():
    ind_conds = (None, 0, Index.equal_to(0))
    val_conds = (None, 1, Value.equal_to(1))
    labels = (None, "my_list_value")

    for i in ind_conds:
        for j in val_conds:
            for k in labels:
                list_val = ListValue(index=i, value=j, label=k)
                assert eval(repr(list_val)) == list_val


def test_evalable_repr_for_simple_map_value():
    key_conds = (None, 0, Key.equal_to(0))
    val_conds = (None, 1, Value.equal_to(1))
    labels = (None, "my_list_value")

    for i in key_conds:
        for j in val_conds:
            for k in labels:
                map_val = MapValue(key=i, value=j, label=k)
                assert eval(repr(map_val)) == map_val


def test_binary_op_equality():
    bo1 = Value.eq(1) & Value.lte(2)
    bo2 = Value.eq(1) & Value.lte(2)
    assert bo1 == bo2

    bo1 = Value.eq(1) | Value.lte(2)
    bo2 = Value.eq(1) | Value.lte(2)
    assert bo1 == bo2

    bo1 = Value.eq(1) ^ Value.lte(2)
    bo2 = Value.eq(1) ^ Value.lte(2)
    assert bo1 == bo2

    bo1 = Value.eq(1) & Value.lte(2) & Value.gt(0)
    bo2 = Value.eq(1) & Value.lte(2) & Value.gt(0)
    assert bo1 == bo2


def test_commutativity_of_binary_ops():
    v1a = Value.lt(2)
    v1b = Value.gt(2)
    v1c = Value.eq(3)

    assert v1a & v1b == v1b & v1a
    assert v1a | v1b == v1b | v1a
    assert v1a ^ v1b == v1b ^ v1a

    assert v1a & (v1b | v1c) == (v1b | v1c) & v1a == (v1c | v1b) & v1a


def test_truthy_falsy_for_integers():
    data = [0, 1, 2]
    assert Value.truthy().filter(data).data == [1, 2]
    assert Value.falsy().filter(data).data == [0]


def test_value_null_condition_list_value():
    assert ListValue() == ListValue(value=NullCondition())


def test_value_null_condition_map_value():
    assert MapValue() == MapValue(value=NullCondition())


def test_raise_on_defined_callable_not_returning_bool():
    def my_callable(x):
        return None

    with pytest.raises(InvalidCallable):
        Value(my_callable).test(1)


def test_raise_on_lambda_callable_not_returning_bool():
    my_callable = lambda x: None
    with pytest.raises(InvalidCallable):
        Value(my_callable).test(1)


def test_is_key_like_condition():
    assert Key.eq(1).is_key_like


def test_is_key_like_condition_binary():
    k1 = Key.eq(1)
    k2 = Key.gt(2)
    assert (k1 | k2).is_key_like


def test_is_key_like_condition_ternary():
    k1 = Key.eq(1)
    k2 = Key.gt(2)
    k3 = Key.lt(10)
    assert (k1 | k2 & k3).is_key_like


def test_is_index_like_condition():
    assert Index.eq(1).is_index_like


def test_is_index_like_condition_binary():
    k1 = Index.eq(1)
    k2 = Index.gt(2)
    assert (k1 | k2).is_index_like


def test_is_index_like_condition_ternary():
    k1 = Index.eq(1)
    k2 = Index.gt(2)
    k3 = Index.lt(10)
    assert (k1 | k2 & k3).is_index_like


def test_is_value_like_condition():
    assert Value.eq(1).is_value_like


def test_is_value_like_condition_binary():
    k1 = Value.eq(1)
    k2 = Value.gt(2)
    assert (k1 | k2).is_value_like


def test_is_value_like_condition_ternary():
    k1 = Value.eq(1)
    k2 = Value.gt(2)
    k3 = Value.lt(10)
    assert (k1 | k2 & k3).is_value_like


def test_raise_on_unknown_spec_key():
    with pytest.raises(MalformedConditionLikeSpec):
        ConditionLike.from_spec({"bad_key": 1})


def test_raise_on_unknown_spec_key_binary_op():
    with pytest.raises(MalformedConditionLikeSpec):
        ConditionLike.from_spec({"or": [{"bad_key": 1}, {"value.eq": 2}]})


def test_raise_on_non_list_argument_to_binary_op():
    with pytest.raises(MalformedConditionLikeSpec):
        ConditionLike.from_spec({"or": {"value.eq": 1, "value.eq": 2}})


def test_raise_on_non_multiple_keys_in_binary_op_spec():
    with pytest.raises(MalformedConditionLikeSpec):
        ConditionLike.from_spec(
            {
                "and": [
                    {
                        "value.lt": 1,
                        "value.gt": 2,
                    }
                ]
            }
        )


def test_raise_on_multiple_keys_in_condition_spec():
    with pytest.raises(MalformedConditionLikeSpec):
        ConditionLike.from_spec({"value.lt": 2, "value.gt": 0})


def test_empty_binary_op_is_null_condition():
    assert ConditionLike.from_spec({"and": []}) == NullCondition()


def test_from_spec_callable_invocation_for_multi_arg_callable():
    assert ConditionLike.from_spec(
        {"value.in_range": {"lower": 1, "upper": 2}}
    ) == ConditionLike.from_spec({"value.in_range": [1, 2]})


def test_KeyDataType_is_key_like():
    assert KeyDataType.equal_to(str).is_key_like


def test_KeyLength_is_key_like():
    assert KeyLength.equal_to(2).is_key_like


def test_KeyDataType_is_key_like():
    assert ValueDataType.equal_to(str).is_value_like


def test_KeyDataType_is_key_like():
    assert ValueLength.equal_to(2).is_value_like


def test_equivalence_of_ConditionLike_from_spec_value_dtype_int_spec():
    assert ConditionLike.from_spec(
        {"value.dtype.eq": "int"}
    ) == ConditionLike.from_spec({"value.dtype.eq": int})


def test_equivalence_of_ConditionLike_from_spec_value_dtype_float_spec():
    assert ConditionLike.from_spec(
        {"value.dtype.eq": "float"}
    ) == ConditionLike.from_spec({"value.dtype.eq": float})


def test_equivalence_of_ConditionLike_from_spec_value_dtype_str_spec():
    assert ConditionLike.from_spec(
        {"value.dtype.eq": "str"}
    ) == ConditionLike.from_spec({"value.dtype.eq": str})


def test_equivalence_of_ConditionLike_from_spec_value_dtype_list_spec():
    assert ConditionLike.from_spec(
        {"value.dtype.eq": "list"}
    ) == ConditionLike.from_spec({"value.dtype.eq": list})


def test_equivalence_of_ConditionLike_from_spec_value_dtype_dict_spec():
    assert ConditionLike.from_spec(
        {"value.dtype.eq": "dict"}
    ) == ConditionLike.from_spec({"value.dtype.eq": dict})


def test_equivalence_of_ConditionLike_from_spec_value_dtype_map_spec():
    assert ConditionLike.from_spec(
        {"value.dtype.eq": "map"}
    ) == ConditionLike.from_spec({"value.dtype.eq": dict})


def test_equivalence_of_ConditionLike_from_spec_type_and_dtype():
    assert ConditionLike.from_spec({"value.type.eq": int}) == ConditionLike.from_spec(
        {"value.dtype.eq": int}
    )


def test_equivalence_of_ConditionLike_from_spec_length_and_len():
    assert ConditionLike.from_spec({"value.length.eq": 2}) == ConditionLike.from_spec(
        {"value.len.eq": 2}
    )


def test_equivalence_of_ConditionLike_from_spec_callable_in_and_in_():
    assert ConditionLike.from_spec({"value.in": [1, 2]}) == ConditionLike.from_spec(
        {"value.in_": [1, 2]}
    )


def test_ConditionLike_from_spec_raise_on_missing_callable():
    with pytest.raises(MalformedConditionLikeSpec):
        ConditionLike.from_spec({"value": 1})


def test_ConditionLike_from_spec_raise_on_missing_callable_with_preprocessor():
    with pytest.raises(MalformedConditionLikeSpec):
        ConditionLike.from_spec({"value.length": 1})


def test_ConditionLike_from_spec_case_insensitivity_datum_type():
    assert (
        ConditionLike.from_spec({"value.eq": 1})
        == ConditionLike.from_spec({"Value.eq": 1})
        == ConditionLike.from_spec({"vAlue.eq": 1})
        == ConditionLike.from_spec({"VALUE.eq": 1})
    )


def test_ConditionLike_from_spec_case_insensitivity_callable_name():
    assert (
        ConditionLike.from_spec({"value.eq": 1})
        == ConditionLike.from_spec({"value.Eq": 1})
        == ConditionLike.from_spec({"value.eQ": 1})
        == ConditionLike.from_spec({"value.EQ": 1})
    )


def test_ConditionLike_from_spec_case_insensitivity_preprocessor_name():
    assert (
        ConditionLike.from_spec({"value.len.eq": 1})
        == ConditionLike.from_spec({"value.Len.eq": 1})
        == ConditionLike.from_spec({"value.lEn.eq": 1})
        == ConditionLike.from_spec({"value.LEN.eq": 1})
    )


def test_ConditionLike_from_spec_single_arg_callable_DataPath():
    assert ConditionLike.from_spec(
        {"value.equal_to": {"path": ("a", "b")}}
    ) == Value.eq(DataPath("a", "b"))


def test_ConditionLike_from_spec_single_arg_callable_DataPath_case_insensitivity():
    assert (
        ConditionLike.from_spec({"value.equal_to": {"path": ("a", "b")}})
        == ConditionLike.from_spec({"value.equal_to": {"Path": ("a", "b")}})
        == ConditionLike.from_spec({"value.equal_to": {"paTh": ("a", "b")}})
        == ConditionLike.from_spec({"value.equal_to": {"PATH": ("a", "b")}})
    )


def test_ConditionLike_from_spec_single_arg_callable_DataPath_map_keys():
    assert ConditionLike.from_spec(
        {"value.equal_to": {"path.map_keys": ("a", "b")}}
    ) == Value.eq(DataPath("a", "b").map_keys())


def test_ConditionLike_from_spec_single_arg_callable_DataPath_map_keys_case_insensitivity():
    assert (
        ConditionLike.from_spec({"value.equal_to": {"path.map_keys": ("a", "b")}})
        == ConditionLike.from_spec({"value.equal_to": {"path.Map_Keys": ("a", "b")}})
        == ConditionLike.from_spec({"value.equal_to": {"path.map_kEys": ("a", "b")}})
        == ConditionLike.from_spec({"value.equal_to": {"path.MAP_KEYS": ("a", "b")}})
    )


def test_ConditionLike_from_spec_single_arg_callable_DataPath_map_values():
    assert ConditionLike.from_spec(
        {"value.equal_to": {"path.map_values": ("a", "b")}}
    ) == Value.eq(DataPath("a", "b").map_values())


def test_ConditionLike_from_spec_single_arg_callable_DataPath_length():
    assert ConditionLike.from_spec(
        {"value.equal_to": {"path.length": ("a", "b")}}
    ) == Value.eq(DataPath("a", "b").length())


def test_ConditionLike_from_spec_single_arg_callable_DataPath_dtype():
    assert ConditionLike.from_spec(
        {"value.equal_to": {"path.dtype": ("a", "b")}}
    ) == Value.eq(DataPath("a", "b").dtype())


def test_equivalence_ConditionLike_from_spec_single_arg_callable_DataPath_dtype_type():
    assert ConditionLike.from_spec(
        {"value.equal_to": {"path.dtype": ("a", "b")}}
    ) == ConditionLike.from_spec({"value.equal_to": {"path.type": ("a", "b")}})


def test_equivalence_ConditionLike_from_spec_single_arg_callable_DataPath_len_length():
    assert ConditionLike.from_spec(
        {"value.equal_to": {"path.len": ("a", "b")}}
    ) == ConditionLike.from_spec({"value.equal_to": {"path.length": ("a", "b")}})


def test_equivalence_ConditionLike_from_spec_multi_arg_callable_DataPath():
    assert ConditionLike.from_spec(
        {
            "value.in_range": {
                "lower": {"path": ("A", "lower")},
                "upper": {"path": ("A", "upper")},
            }
        }
    ) == Value.in_range(lower=DataPath("A", "lower"), upper=DataPath("A", "upper"))


def test_ConditionLike_from_spec_DataPath_escape():
    assert ConditionLike.from_spec(
        {"value.equal_to": {r"\path": ["A", "B"]}}
    ) == Value.equal_to({"path": ["A", "B"]})


def test_ConditionLike_from_spec_DataPath_escape_multi_item():
    assert ConditionLike.from_spec(
        {"value.equal_to": {r"\path": ["A", "B"], "key": "val"}}
    ) == Value.equal_to({"path": ["A", "B"], "key": "val"})


def test_ConditionLike_from_spec_DataPath_escape_slashed():
    assert ConditionLike.from_spec(
        {"value.equal_to": {r"\\path": ["A", "B"]}}
    ) == Value.equal_to({"\path": ["A", "B"]})


def test_ConditionLike_from_spec_DataPath_map_values_escape():
    assert ConditionLike.from_spec(
        {"value.equal_to": {r"\path.map_values": ["A", "B"]}}
    ) == Value.equal_to({"path.map_values": ["A", "B"]})


def test_ConditionLike_from_spec_equivalence_value_equal_to():
    assert ConditionLike.from_spec({"value.equal_to": 4}) == Value.equal_to(4)


def test_ConditionLike_from_spec_dtype_case_insensitivity():
    assert (
        ConditionLike.from_spec({"value.dtype.equal_to": "str"})
        == ConditionLike.from_spec({"value.dtype.equal_to": "STR"})
        == ConditionLike.from_spec({"value.dtype.equal_to": "sTr"})
    )


def test_ConditionLike_from_spec_dtype_native_type_equivalence():
    assert ConditionLike.from_spec(
        {"value.dtype.equal_to": "str"}
    ) == ConditionLike.from_spec({"value.dtype.equal_to": str})


def test_ConditionLike_from_spec_equivalence_is_instance_single_cls():
    assert ConditionLike.from_spec({"value.is_instance": ["str"]}) == Value.is_instance(
        str
    )


def test_ConditionLike_from_spec_equivalence_is_instance_multiple_cls():
    assert ConditionLike.from_spec(
        {"value.is_instance": ["str", "int"]}
    ) == Value.is_instance(str, int)


def test_ConditionLike_from_spec_equivalence_is_instance_native_type():
    assert ConditionLike.from_spec(
        {"value.is_instance": ["str", "int"]}
    ) == ConditionLike.from_spec({"value.is_instance": [str, int]})


def test_to_json_like_round_trip_null():
    c1 = NullCondition()
    c1_js = c1.to_json_like()
    assert ConditionLike.from_spec(c1_js) == c1


def test_to_json_like_round_trip_value_equal_to():
    c1 = Value.equal_to(1)
    c1_js = c1.to_json_like()
    assert ConditionLike.from_spec(c1_js) == c1


def test_to_json_like_round_trip_value_dtype_int_equal_to():
    c1 = Value.dtype.equal_to(int)
    c1_js = c1.to_json_like()
    assert ConditionLike.from_spec(c1_js) == c1


def test_to_json_like_round_trip_value_dtype_str_equal_to():
    c1 = Value.dtype.equal_to(str)
    c1_js = c1.to_json_like()
    assert ConditionLike.from_spec(c1_js) == c1


def test_to_json_like_round_trip_value_dtype_path_equal_to():
    c1 = Value.dtype.equal_to(pathlib.Path)
    c1_js = c1.to_json_like()
    assert ConditionLike.from_spec(c1_js) == c1


def test_to_json_like_round_trip_value_length_equal_to():
    c1 = Value.length.equal_to(2)
    c1_js = c1.to_json_like()
    assert ConditionLike.from_spec(c1_js) == c1


def test_to_json_like_round_trip_key_equal_to():
    c1 = Key.equal_to(2)
    c1_js = c1.to_json_like()
    assert ConditionLike.from_spec(c1_js) == c1


def test_to_json_like_round_trip_index_equal_to():
    c1 = Index.equal_to(2)
    c1_js = c1.to_json_like()
    assert ConditionLike.from_spec(c1_js) == c1


@pytest.mark.parametrize("binary_op", ("and", "or", "xor"))
def test_to_json_like_round_trip_binary(binary_op):
    cnd_js = {binary_op: [{"key.equal_to": 0}, {"value.dtype.equal_to": "dict"}]}
    cnd = Condition.from_json_like(cnd_js)
    assert cnd.to_json_like() == cnd_js
