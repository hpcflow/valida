import pytest

from valida.conditions import Key, Index, Value
from valida.datapath import DataPath, MapValue, ListValue


def test_alternative_map_value_key_spec():

    mv1 = MapValue("A")
    mv2 = MapValue(key="A")
    mv3 = MapValue(Key.equal_to("A"))
    mv4 = MapValue(condition=Key.equal_to("A"))

    assert mv1 == mv2 == mv3 == mv4


def test_alternative_map_value_key_value_spec():

    c2 = Value.lte(3)
    mk1 = Key.in_(["a", "b", "c"])
    mv1 = MapValue(key=mk1, value=c2)
    mv2 = MapValue(condition=(mk1 & c2))

    assert mv1 == mv2


def test_map_value_filter_on_combined_key_value():
    my_dict = {"a": 1, "b": 4, "c": 3, "d": 2}
    mv1 = MapValue(
        key=Key.in_(["a", "b", "c"]),
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

    path1 = MapValue(Key.eq("A1") | Key.eq("A2")) / MapValue("X1")
    assert path1.get_data(data) == [1, 2]

    path2 = DataPath(MapValue())
    assert path2.get_data(data) == [{"X1": 1}, {"X1": 2}, {"X1": 3}]
