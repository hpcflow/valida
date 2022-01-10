import pytest

from valida.conditions import Key, Index, Value
from valida.datapath import DataPath, MapValue, ListValue


def test_alternative_map_value_key_spec():

    mv1 = MapValue("A")
    mv2 = MapValue(Value.equal_to("A"))
    mv3 = MapValue(key="A")
    mv4 = MapValue(key=Value.equal_to("A"))
    mv5 = MapValue(condition=Key.equal_to("A"))

    assert mv1 == mv2 == mv3 == mv4 == mv5


def test_alternative_map_value_key_value_spec():

    in_arg = ["a", "b", "c"]
    lte_arg = 3

    c1 = Value.in_(in_arg)
    c2 = Value.lte(lte_arg)
    mk1 = Key.in_(in_arg)

    mv1 = MapValue(key=c1, value=c2)
    mv2 = MapValue(key=mk1, value=c2)
    mv3 = MapValue(key=c1.to_key(), value=c2)
    mv4 = MapValue(condition=(mk1 & c2))

    assert mv1 == mv2 == mv3 == mv4


def test_map_value_filter_on_combined_key_value():
    my_dict = {"a": 1, "b": 4, "c": 3, "d": 2}
    mv1 = MapValue(
        key=Value.in_(["a", "b", "c"]),
        value=Value.lte(3),
    )
    assert mv1.filter(my_dict).get_data() == [1, 3]


def test_get_data_map_values_only():

    data = {
        "A1": {
            "X1": 1,
        },
        "A2": {
            "X1": 2,
        },
        "A3": {
            "X1": 3,
        },
    }

    path1 = MapValue() / MapValue()
    assert path1.get_data(data) == [1, 2, 3]

    path1 = MapValue(Value.eq("A1") | Value.eq("A2")) / MapValue("X1")
    assert path1.get_data(data) == [1, 2]

    path2 = DataPath(MapValue())
    assert path2.get_data(data) == [{"X1": 1}, {"X1": 2}, {"X1": 3}]
