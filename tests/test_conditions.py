import pytest

from valida.conditions import (
    Value,
    Key,
    Index,
    Length,
    DType,
    NullCondition,
    And,
    Or,
    Xor,
)


def test_is_like_methods_on_single_condition():

    vc1 = Value.equal_to(1)
    kc1 = Key.equal_to(1)
    ic1 = Index.equal_to(1)

    assert vc1.is_value_like == True
    assert vc1.is_key_like == False
    assert vc1.is_index_like == False

    assert kc1.is_key_like == True
    assert kc1.is_value_like == False
    assert kc1.is_index_like == False

    assert ic1.is_index_like == True
    assert ic1.is_value_like == False
    assert ic1.is_key_like == False


def test_is_like_methods_on_binary_condition_single_datum_type():

    vc1 = Value.equal_to(1)
    vc2 = Value.equal_to(2)

    kc1 = Key.equal_to(1)
    kc2 = Key.equal_to(2)

    ic1 = Index.equal_to(1)
    ic2 = Index.equal_to(2)

    vcA = vc1 | vc2
    kcA = kc1 | kc2
    icA = ic1 | ic2

    assert vcA.is_value_like == True
    assert vcA.is_key_like == False
    assert vcA.is_index_like == False

    assert kcA.is_value_like == False
    assert kcA.is_key_like == True
    assert kcA.is_index_like == False

    assert icA.is_value_like == False
    assert icA.is_key_like == False
    assert icA.is_index_like == True


def test_is_like_methods_on_binary_conditions_mixed_datum_types():

    vc1 = Value.equal_to(1)
    kc1 = Key.equal_to(1)
    ic1 = Index.equal_to(1)

    mc1 = vc1 | kc1
    mc2 = vc1 | ic1

    assert mc1.is_value_like == True
    assert mc1.is_key_like == False
    assert mc1.is_index_like == False

    assert mc2.is_value_like == True
    assert mc2.is_key_like == False
    assert mc2.is_index_like == False


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


def test_from_pre_processor_class_value_length():
    assert Value.length == Value._from_pre_processor_class(Length)


def test_from_pre_processor_class_value_dtype():
    assert Value.dtype == Value._from_pre_processor_class(DType)


def test_from_pre_processor_class_key_dtype():
    assert Key.dtype == Key._from_pre_processor_class(DType)


def test_value_to_key():
    assert Value.equal_to(1).to_key() == Key.equal_to(1)


def test_value_length_to_key():
    assert Value.length.equal_to(1).to_key() == Key.length.equal_to(1)


def test_value_dtype_to_key():
    assert Value.dtype.equal_to(str).to_key() == Key.dtype.equal_to(str)


def test_value_length_to_index_raises_type_error():
    with pytest.raises(TypeError):
        Value.length.equal_to(1).to_index()


def test_value_dtype_to_index_raises_type_error():
    with pytest.raises(TypeError):
        Value.dtype.equal_to(str).to_index()


def test_null_condition_does_not_generate_binary_condition():
    c1 = Value.equal_to(1)
    assert And(c1, NullCondition()) == c1
    assert And(NullCondition(), c1) == c1
    assert Or(c1, NullCondition()) == c1
    assert Or(NullCondition(), c1) == c1
    assert Xor(c1, NullCondition()) == c1
    assert Xor(NullCondition(), c1) == c1


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
