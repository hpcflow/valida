import pytest

from valida.conditions import (
    Value,
    Key,
    Index,
    NullCondition,
    ConditionAnd,
    ConditionOr,
    ConditionXor,
)
from valida.datapath import ListValue, MapValue
from valida.errors import InvalidCallable


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
    assert NullCondition().filter(my_list).get_data() == my_list


def test_null_condition_filter_includes_all_map_items():
    my_dict = {"a": 1, "b": 2, "c": 3}
    assert NullCondition().filter(my_dict).get_data() == list(my_dict.values())


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
    assert Value.truthy().filter(data).get_data() == [1, 2]
    assert Value.falsy().filter(data).get_data() == [0]


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
