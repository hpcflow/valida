import pytest

from valida.conditions import Key, Index, Value
from valida.datapath import (
    ContainerValue,
    DataPath,
    MapOrListValue,
    MapValue,
    ListValue,
)
from valida.data import Data


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
    assert mv1.filter(my_dict).data == [1, 3]


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


def test_data_get_concrete_path_string_key():
    data = Data({"a1": {"b1": 1, "b2": [1, 2, 3]}})
    path = DataPath("a1")
    assert data.get(path) == {"b1": 1, "b2": [1, 2, 3]}


def test_data_get_non_concrete_path_map_value():
    data = Data({"a1": {"b1": 1, "b2": [1, 2, 3]}})
    path = DataPath(MapValue("a1"))
    assert data.get(path) == [{"b1": 1, "b2": [1, 2, 3]}]


def test_data_get_non_concrete_path_string_key_and_list_value():
    data = Data({"a1": {"b1": 1, "b2": [1, 2, 3]}})
    path = DataPath("a1", "b2", ListValue())
    assert data.get(path) == [1, 2, 3]


def test_data_get_non_concrete_path_string_key_and_map_value():
    data = Data({"a1": {"b1": 1, "b2": [1, 2, 3]}})
    path = DataPath("a1", MapValue())
    assert data.get(path) == [1, [1, 2, 3]]


def test_equivalance_data_get_datapath_and_datapath_get_data():
    data = Data({"a1": {"b1": 1, "b2": [1, 2, 3]}})
    path = DataPath("a1")
    assert data.get(path) == path.get_data(data)


def test_coercion_to_data_path_in_data_get_single_part_path():
    data = Data({"a1": {"b1": 1, "b2": [1, 2, 3]}})
    assert data.get("a1") == data.get(DataPath("a1"))


def test_coercion_to_data_path_in_data_get_multi_part_path():
    data = Data({"a1": {"b1": 1, "b2": [1, 2, 3]}})
    assert data.get("a1", "b1") == data.get(DataPath("a1", "b1"))


def test_coercion_to_data_path_in_data_get_with_map_value():
    data = Data({"a1": {"b1": 1, "b2": [1, 2, 3]}})
    assert data.get(MapValue("a1")) == data.get(DataPath(MapValue("a1")))


def test_coercion_to_data_path_in_data_get_with_list_value():
    data = Data({"a1": {"b1": 1, "b2": [1, 2, 3]}})
    assert data.get("a1", "b2", ListValue(0)) == data.get(
        DataPath("a1", "b2", ListValue(0))
    )


def test_composure_of_datapath_from_slash_operator():
    assert MapValue("A") / MapValue("B") / ListValue() == DataPath(
        MapValue("A"), MapValue("B"), ListValue()
    )


def test_data_path_get_on_list_value_data_type_condition():
    my_data = {"A": {"B": [1, 2.5, 3]}}
    data_path = MapValue("A") / MapValue("B") / ListValue(value=Value.dtype.eq(int))
    assert data_path.get_data(my_data) == [1, 3]


def test_data_path_get_on_map_value_data_type_condition():
    my_data = {"A": {"b1": 1, "b2": 2.5, "b3": 4}}
    data_path = MapValue() / MapValue(value=Value.dtype.eq(int))
    assert data_path.get_data(my_data) == [1, 4]


def test_equivalence_of_data_path_get_data_with_data_arg_and_list_arg_single_list_value():
    dat_1 = [1, 2, 3]
    dat_2 = Data(dat_1)
    data_path = DataPath(ListValue(0))
    assert data_path.get_data(dat_1) == data_path.get_data(dat_2)


def test_equivalence_of_data_path_get_data_with_data_arg_and_map_arg_single_map_value():
    dat_1 = {0: 8, 1: 9, 2: 10}
    dat_2 = Data(dat_1)
    data_path = DataPath(MapValue(0))
    assert data_path.get_data(dat_1) == data_path.get_data(dat_2)


def test_correct_return_from_ambiguous_container_value_with_list_arg():
    dat = [1, 2, 3]
    data_path = DataPath(2)
    assert data_path.get_data(dat) == 3


def test_correct_return_from_ambiguous_container_value_with_Data_list_arg():
    dat = Data([1, 2, 3])
    data_path = DataPath(2)
    assert data_path.get_data(dat) == 3


def test_correct_return_from_ambiguous_container_value_with_map_arg():
    dat = {0: 8, 1: 9, 2: 10}
    data_path = DataPath(2)
    assert data_path.get_data(dat) == 10


def test_correct_return_from_ambiguous_container_value_with_Data_map_arg():
    dat = Data({0: 8, 1: 9, 2: 10})
    data_path = DataPath(2)
    assert data_path.get_data(dat) == 10


def test_get_data_from_nested_list():
    data = Data([[0, 1, 2], [3, [4, 5, 6]]])
    path = DataPath(1, 1, 0)
    assert data.get(path) == 4


def test_equivalence_of_from_specs():
    assert DataPath.from_part_specs("A", 0, "B") == DataPath("A", 0, "B")


def test_equivalence_of_from_specs_with_condition_less_MapValue():
    assert DataPath.from_part_specs("A", 0, {"type": "map_value"}) == DataPath(
        "A", 0, MapValue()
    )


def test_equivalence_of_from_specs_with_condition_less_ListValue():
    assert DataPath.from_part_specs("A", 0, {"type": "list_value"}) == DataPath(
        "A", 0, ListValue()
    )


def test_equivalence_ContainerValue_from_spec_with_ListValue():
    assert (
        ContainerValue.from_spec(
            {
                "type": "list_value",
                "value": {"value.eq": 1},
            }
        )
        == ListValue(value=Value.eq(1))
    )


def test_equivalence_ContainerValue_from_spec_with_MapValue():
    assert (
        ContainerValue.from_spec(
            {
                "type": "map_value",
                "value": {"value.eq": 1},
            }
        )
        == MapValue(value=Value.eq(1))
    )


def test_DataPath_is_concrete_true():
    assert DataPath("A", 0, "B").is_concrete == True


def test_DataPath_is_concrete_false():
    assert DataPath("A", 0, MapValue("B")).is_concrete == False


def test_DataPath_from_specs_is_concrete_true():
    assert DataPath.from_part_specs("A", 0, "B").is_concrete == True


def test_DataPath_from_specs_is_concrete_false():
    assert (
        DataPath.from_part_specs(
            "A", 0, {"type": "map_value", "key.equal_to": "B"}
        ).is_concrete
        == False
    )


def test_equivalence_of_ContainerValue_from_spec_with_shorthand_key_condition():
    assert ContainerValue.from_spec(
        {
            "type": "map_value",
            "key": {
                "key.dtype.equal_to": str,
            },
        }
    ) == ContainerValue.from_spec(
        {
            "type": "map_value",
            "key.dtype.equal_to": str,
        }
    )


def test_MapValue_raise_on_incompatible_key_condition_with_value():
    with pytest.raises(TypeError):
        MapValue(key=Value.equal_to(1))


def test_MapValue_raise_on_incompatible_key_condition_with_index():
    with pytest.raises(TypeError):
        MapValue(key=Index.equal_to(1))


def test_MapValue_raise_on_incompatible_value_condition_with_key():
    with pytest.raises(TypeError):
        MapValue(value=Key.equal_to(1))


def test_MapValue_raise_on_incompatible_key_condition_with_index():
    with pytest.raises(TypeError):
        MapValue(value=Index.equal_to(1))


def test_ListValue_raise_on_incompatible_index_condition_with_value():
    with pytest.raises(TypeError):
        ListValue(index=Value.equal_to(1))


def test_ListValue_raise_on_incompatible_index_condition_with_key():
    with pytest.raises(TypeError):
        ListValue(index=Key.equal_to(1))


def test_ListValue_raise_on_incompatible_value_condition_with_key():
    with pytest.raises(TypeError):
        ListValue(value=Key.equal_to(1))


def test_ListValue_raise_on_incompatible_value_condition_with_index():
    with pytest.raises(TypeError):
        ListValue(value=Index.equal_to(1))


def test_ContainerValue_from_spec_raise_on_MapValue_with_incompatible_condition_with_index():
    with pytest.raises(ValueError):
        ContainerValue.from_spec({"type": "map_value", "index": {"index.equal_to": 1}})


def test_ContainerValue_from_spec_raise_on_ListValue_with_incompatible_condition_with_key():
    with pytest.raises(ValueError):
        ContainerValue.from_spec({"type": "list_value", "key": {"key.equal_to": 1}})


def test_ContainerValue_from_spec_raise_on_MapValue_with_incompatible_key_condition_with_value():
    with pytest.raises(ValueError):
        ContainerValue.from_spec(
            {
                "type": "map_value",
                "key": {"value.equal_to": 1},
            }
        )


def test_ContainerValue_from_spec_raise_on_ListValue_with_incompatible_index_condition_with_value():
    with pytest.raises(ValueError):
        ContainerValue.from_spec(
            {
                "type": "list_value",
                "index": {"value.equal_to": 1},
            }
        )


def test_Data_get_DataPath_expected_return_with_MapOrListValue():

    data = Data(
        {
            "A": [900, 910, 920],
            "B": {"b1": 10, "b2": 11},
        }
    )
    path = DataPath(
        MapValue(),
        MapOrListValue(key=Key.in_(["b1"]), index=Index.in_([0, 2])),
    )
    assert data.get(path) == [900, 920, 10]


def test_expected_return_Data_get_with_return_paths():
    data = Data(
        {
            "A1": {
                "A1B1": {"A1B1C1": 1},
                "A1B2": {
                    "A1B2C2": 2,
                    "A1B2C3": 3,
                },
            },
            "A2": {
                "A2B1": {
                    "A2B1C4": 4,
                    "A2B1C5": 5,
                    "A2B1C6": 6,
                },
            },
        }
    )
    path = DataPath(MapValue(), MapValue(), MapValue())
    sub_data = data.get(path, return_paths=True)

    assert sub_data == [
        (1, ("A1", "A1B1", "A1B1C1")),
        (2, ("A1", "A1B2", "A1B2C2")),
        (3, ("A1", "A1B2", "A1B2C3")),
        (4, ("A2", "A2B1", "A2B1C4")),
        (5, ("A2", "A2B1", "A2B1C5")),
        (6, ("A2", "A2B1", "A2B1C6")),
    ]


def test_expected_return_Data_get_with_DataPath_no_args_with_return_paths_true():
    dat = {"A": [900, 910, 920]}
    data = Data(dat)
    assert data.get(DataPath(), return_paths=True) == (dat, ())


def test_expected_return_Data_get_with_DataPath_no_args_with_return_paths_false():
    dat = {"A": [900, 910, 920]}
    data = Data(dat)
    assert data.get(DataPath(), return_paths=False) == dat


def test_expected_return_Data_get_with_no_args_with_return_paths_true():
    dat = {"A": [900, 910, 920]}
    data = Data(dat)
    assert data.get(return_paths=True) == (dat, ())


def test_expected_return_Data_get_with_no_args_with_return_paths_false():
    dat = {"A": [900, 910, 920]}
    data = Data(dat)
    assert data.get(return_paths=False) == dat


def test_expected_return_Data_get_with_DataPath_concrete_path_with_return_paths_true():
    dat = {"A": [900, 910, 920]}
    data = Data(dat)
    assert data.get(DataPath("A"), return_paths=True) == (dat["A"], ("A",))


def test_expected_return_Data_get_with_DataPath_concrete_path_with_return_paths_false():
    dat = {"A": [900, 910, 920]}
    data = Data(dat)
    assert data.get(DataPath("A"), return_paths=False) == dat["A"]


def test_expected_return_Data_get_with_concrete_path_with_return_paths_true():
    dat = {"A": [900, 910, 920]}
    data = Data(dat)
    assert data.get("A", return_paths=True) == (dat["A"], ("A",))


def test_expected_return_Data_get_with_concrete_path_with_return_paths_false():
    dat = {"A": [900, 910, 920]}
    data = Data(dat)
    assert data.get("A", return_paths=False) == dat["A"]


def test_expected_return_Data_get_with_DataPath_non_concrete_path_with_return_paths_true():
    dat = {"A": [900, 910, 920]}
    data = Data(dat)
    assert data.get(DataPath(MapValue("A")), return_paths=True) == [(dat["A"], ("A",))]


def test_expected_return_Data_get_with_DataPath_non_concrete_path_with_return_paths_false():
    dat = {"A": [900, 910, 920]}
    data = Data(dat)
    assert data.get(DataPath(MapValue("A")), return_paths=False) == [dat["A"]]


def test_expected_return_Data_get_with_non_concrete_path_with_return_paths_true():
    dat = {"A": [900, 910, 920]}
    data = Data(dat)
    assert data.get(MapValue("A"), return_paths=True) == [(dat["A"], ("A",))]


def test_expected_return_Data_get_with_non_concrete_path_with_return_paths_false():
    dat = {"A": [900, 910, 920]}
    data = Data(dat)
    assert data.get(MapValue("A"), return_paths=False) == [dat["A"]]


def test_expected_return_map_Data_get_with_non_existent_non_concrete_path_with_return_paths_true():
    assert Data({"A": 1}).get(MapValue("B"), return_paths=True) == []


def test_expected_return_map_Data_get_with_non_existent_non_concrete_path_with_return_paths_false():
    assert Data({"A": 1}).get(MapValue("B"), return_paths=False) == []


def test_expected_return_map_Data_get_with_non_existent_concrete_path_with_return_paths_true():
    assert Data({"A": 1}).get("B", return_paths=True) == None


def test_expected_return_map_Data_get_with_non_existent_concrete_path_with_return_paths_false():
    assert Data({"A": 1}).get("B", return_paths=False) == None


def test_expected_return_list_Data_get_with_non_existent_non_concrete_MapValue_path():
    assert Data([9, 8, 7]).get(MapValue("A")) == []


def test_expected_return_list_Data_get_with_non_existent_concrete_MapValue_path():
    assert Data([9, 8, 7]).get("A") == None


def test_expected_return_map_Data_get_with_non_existent_non_concrete_ListValue_path():
    assert Data({"A": 1}).get(ListValue(0)) == []


def test_expected_return_map_Data_get_with_non_existent_concrete_ListValue_path():
    assert Data({"A": 1}).get(0) == None


def test_expected_return_DataPath_datum_type_map_map_keys_concrete_path():
    data = Data({"c": {"C1": 19, "C2": 20}})
    path = DataPath("c").map_keys()
    assert data.get(path) == ["C1", "C2"]


def test_expected_return_DataPath_datum_type_map_map_values_concrete_path():
    data = Data({"c": {"C1": 19, "C2": 20}})
    path = DataPath("c").map_values()
    assert data.get(path) == [19, 20]


def test_expected_return_DataPath_datum_type_map_length_concrete_path():
    data = Data({"c": {"C1": 19, "C2": 20}})
    path = DataPath("c").length()
    assert data.get(path) == 2


def test_expected_return_DataPath_datum_type_map_dtpye_concrete_path():
    data = Data({"c": {"C1": 19, "C2": 20}})
    path = DataPath("c").dtype()
    assert data.get(path) == dict


def test_expected_return_DataPath_datum_type_list_length_concrete_path():
    data = Data({"c": [19, 20, 21]})
    path = DataPath("c").length()
    assert data.get(path) == 3


def test_expected_return_DataPath_datum_type_list_dtpye_concrete_path():
    data = Data({"c": [19, 20, 21]})
    path = DataPath("c").dtype()
    assert data.get(path) == list


def test_expected_return_DataPath_datum_type_str_length_concrete_path():
    data = Data({"c": "hey!"})
    path = DataPath("c").length()
    assert data.get(path) == 4


def test_expected_return_DataPath_datum_type_str_dtpye_concrete_path():
    data = Data({"c": "hey!"})
    path = DataPath("c").dtype()
    assert data.get(path) == str


def test_expected_return_DataPath_datum_type_map_map_keys_non_concrete_path():
    data = Data({"c": {"C1": 19, "C2": 20}})
    path = DataPath(MapValue("c")).map_keys()
    assert data.get(path) == [["C1", "C2"]]


def test_expected_return_DataPath_datum_type_map_map_values_non_concrete_path():
    data = Data({"c": {"C1": 19, "C2": 20}})
    path = DataPath(MapValue("c")).map_values()
    assert data.get(path) == [[19, 20]]


def test_expected_return_DataPath_datum_type_map_length_non_concrete_path():
    data = Data({"c": {"C1": 19, "C2": 20}})
    path = DataPath(MapValue("c")).length()
    assert data.get(path) == [2]


def test_expected_return_DataPath_datum_type_map_dtpye_non_concrete_path():
    data = Data({"c": {"C1": 19, "C2": 20}})
    path = DataPath(MapValue("c")).dtype()
    assert data.get(path) == [dict]


def test_expected_return_DataPath_datum_type_list_length_non_concrete_path():
    data = Data({"c": [19, 20, 21]})
    path = DataPath(MapValue("c")).length()
    assert data.get(path) == [3]


def test_expected_return_DataPath_datum_type_list_dtpye_non_concrete_path():
    data = Data({"c": [19, 20, 21]})
    path = DataPath(MapValue("c")).dtype()
    assert data.get(path) == [list]


def test_expected_return_DataPath_datum_type_str_length_non_concrete_path():
    data = Data({"c": "hey!"})
    path = DataPath(MapValue("c")).length()
    assert data.get(path) == [4]


def test_expected_return_DataPath_datum_type_str_dtpye_non_concrete_path():
    data = Data({"c": "hey!"})
    path = DataPath(MapValue("c")).dtype()
    assert data.get(path) == [str]


def test_expected_return_DataPath_datum_type_map_map_keys_empty_path():
    data = Data({"C1": 19, "C2": 20})
    path = DataPath().map_keys()
    assert data.get(path) == ["C1", "C2"]


def test_expected_return_DataPath_datum_type_map_map_values_empty_path():
    data = Data({"C1": 19, "C2": 20})
    path = DataPath().map_values()
    assert data.get(path) == [19, 20]


def test_expected_return_DataPath_datum_type_map_length_empty_path():
    data = Data({"C1": 19, "C2": 20})
    path = DataPath().length()
    assert data.get(path) == 2


def test_expected_return_DataPath_datum_type_map_dtpye_empty_path():
    data = Data({"C1": 19, "C2": 20})
    path = DataPath().dtype()
    assert data.get(path) == dict


def test_expected_return_DataPath_datum_type_list_length_empty_path():
    data = Data([19, 20, 21])
    path = DataPath().length()
    assert data.get(path) == 3


def test_expected_return_DataPath_datum_type_list_dtpye_empty_path():
    data = Data([19, 20, 21])
    path = DataPath().dtype()
    assert data.get(path) == list


def test_expected_return_DataPath_datum_type_str_length_empty_path():
    data = Data({"c": "hey!"})
    path = DataPath().length()
    assert data.get(path) == 1


def test_expected_return_DataPath_datum_type_str_dtpye_empty_path():
    data = Data({"c": "hey!"})
    path = DataPath().dtype()
    assert data.get(path) == dict


def test_equivalence_of_DataPath_source_data_placement_empty_path_list():
    data = [1, 2, 3]
    assert DataPath(source_data=data).get_data() == DataPath().get_data(data)


def test_equivalence_of_DataPath_source_data_placement_empty_path_Data_list():
    data = Data([1, 2, 3])
    assert (
        DataPath(source_data=data).get_data() == DataPath().get_data(data) == data.get()
    )


def test_equivalence_of_DataPath_source_data_placement_empty_path_map():
    data = {"a": 1, "b": 2, "c": 3}
    assert DataPath(source_data=data).get_data() == DataPath().get_data(data)


def test_equivalence_of_DataPath_source_data_placement_empty_path_Data_map():
    data = Data({"a": 1, "b": 2, "c": 3})
    assert (
        DataPath(source_data=data).get_data() == DataPath().get_data(data) == data.get()
    )


def test_equivalence_of_DataPath_source_data_placement_non_concrete_path_map():
    path_comps = (MapValue("A"),)
    data = {"A": {"a": 1, "b": 2, "c": 3}}
    assert DataPath(*path_comps, source_data=data).get_data() == DataPath(
        *path_comps
    ).get_data(data)


def test_equivalence_of_DataPath_source_data_placement_concrete_path_map():
    path_comps = ("A",)
    data = {"A": {"a": 1, "b": 2, "c": 3}}
    assert DataPath(*path_comps, source_data=data).get_data() == DataPath(
        *path_comps
    ).get_data(data)


def test_equivalence_of_DataPath_source_data_placement_non_concrete_path_Data_map():
    path_comps = (MapValue("A"),)
    data = Data({"A": {"a": 1, "b": 2, "c": 3}})
    assert (
        DataPath(*path_comps, source_data=data).get_data()
        == DataPath(*path_comps).get_data(data)
        == data.get(*path_comps)
    )


def test_equivalence_of_DataPath_source_data_placement_concrete_path_Data_map():
    path_comps = ("A",)
    data = Data({"A": {"a": 1, "b": 2, "c": 3}})
    assert (
        DataPath(*path_comps, source_data=data).get_data()
        == DataPath(*path_comps).get_data(data)
        == data.get(*path_comps)
    )


def test_equivalence_DataPath_get_data_DATUM_TYPE_and_MULTI_TYPE_order():
    data = Data({"c": {"C1": 19, "C2": 20}})
    path1 = DataPath(MapValue("c")).map_keys().single()
    path2 = DataPath(MapValue("c")).single().map_keys()
    assert path1.get_data(data) == path2.get_data(data)


def test_equivalence_DataPath_get_data_return_of_MULTI_TYPE_first_last_single_for_length_one_match():
    data = Data({"c": {"C1": 19, "C2": 20}})
    path1 = DataPath(MapValue("c")).first()
    path2 = DataPath(MapValue("c")).last()
    path3 = DataPath(MapValue("c")).single()
    assert path1.get_data(data) == path2.get_data(data) == path3.get_data(data)


def test_DataPath_get_data_raise_on_MULTI_TYPE_single_with_multiple_matches():
    data = Data(
        {
            "c": {"C1": 19, "C2": 20},
            "d": {"D1": 21, "D2": 22},
        }
    )
    path = DataPath(MapValue(Key.in_(["c", "d"]))).single()
    with pytest.raises(ValueError):
        path.get_data(data)


def test_expected_return_DataPath_get_data_MULTI_TYPE_first():

    data = Data(
        {
            "c": [1, 2, 3],
            "d": [4, 5, 6],
        }
    )
    path = DataPath(MapValue(Key.in_(["c", "d"]))).first()
    assert path.get_data(data) == [1, 2, 3]


def test_expected_return_DataPath_get_data_MULTI_TYPE_last():

    data = Data(
        {
            "c": [1, 2, 3],
            "d": [4, 5, 6],
        }
    )
    path = DataPath(MapValue(Key.in_(["c", "d"]))).last()
    assert path.get_data(data) == [4, 5, 6]


def test_DataPath_raise_on_concrete_path_with_MULTI_TYPE_single():
    with pytest.raises(ValueError):
        DataPath(1).single()


def test_DataPath_raise_on_concrete_path_with_MULTI_TYPE_first():
    with pytest.raises(ValueError):
        DataPath(1).first()


def test_DataPath_raise_on_concrete_path_with_MULTI_TYPE_last():
    with pytest.raises(ValueError):
        DataPath(1).last()


def test_DataPath_raise_on_concrete_path_with_MULTI_TYPE_all():
    with pytest.raises(ValueError):
        DataPath(1).all()


def test_expected_return_DataPath_get_data_MULTI_TYPE_DATUM_TYPE_combo_map_keys_single():
    data = Data({"c": {"C1": 19, "C2": 20}})
    path = DataPath(MapValue("c")).map_keys().single()
    assert path.get_data(data) == ["C1", "C2"]


def test_expected_return_DataPath_get_data_MULTI_TYPE_DATUM_TYPE_combo_map_values_last():
    data = Data({"c": {"C1": 19, "C2": 20}})
    path = DataPath(MapValue("c")).map_values().last()
    assert path.get_data(data) == [19, 20]


def test_expected_return_DataPath_get_data_MULTI_TYPE_DATUM_TYPE_combo_length_all():
    data = Data(
        {
            "c": {"C1": 19, "C2": 20},
            "d": {"D1": 21, "D2": 22, "D3": 23},
        }
    )
    path = DataPath(MapValue(Key.in_(("c", "d")))).length().all()
    assert path.get_data(data) == [2, 3]


def test_expected_return_DataPath_get_data_MULTI_TYPE_DATUM_TYPE_combo_length_first():
    data = Data(
        {
            "c": {"C1": 19, "C2": 20},
            "d": {"D1": 21, "D2": 22, "D3": 23},
        }
    )
    path = DataPath(MapValue(Key.in_(("c", "d")))).length().first()
    assert path.get_data(data) == 2


def test_expected_return_DataPath_from_str():
    assert DataPath.from_str("a/b/c") == DataPath("a", "b", "c")


def test_expected_return_DataPath_from_str_custom_delimiter():
    assert DataPath.from_str("a.b.c", delimiter=".") == DataPath("a", "b", "c")


def test_expected_return_DataPath_from_str_ambiguous_integer():
    assert DataPath.from_str("a/0") == DataPath(
        "a", MapOrListValue(key=Key.in_(("0", 0)), index=0)
    )


def test_expected_return_DataPath_from_str_empty_str():
    assert DataPath.from_str("") == DataPath()


def test_expected_return_DataPath_from_str_None():
    assert DataPath.from_str(None) == DataPath()


def test_equivalent_DataPath_from_str_concrete_path_get_data():
    data = Data({"A": {"B": [9, 8, 7]}})
    path1 = DataPath("A", "B")
    path2 = DataPath.from_str("A/B")
    assert path1.get_data(data) == path2.get_data(data)


def test_equivalent_DataPath_from_str_non_concrete_path_get_data():

    data = Data({"A": {"B": [9, 8, 7]}})
    # coerce to a non-concrete with the MapValue, since `DataPath.from_str` produces a
    # non-concrete path in this case due to the ambiguity of the integer part
    path1 = DataPath(MapValue("A"), "B", 2)
    path2 = DataPath.from_str("A/B/2")

    assert path1.get_data(data) == path2.get_data(data)


def test_equivalence_DataPath_from_spec_DATUM_TYPE_MULTI_TYPE_order():
    path_parts = (MapValue("a"), "b")
    assert DataPath.from_spec(
        {"path.single.map_keys": path_parts}
    ) == DataPath.from_spec({"path.map_keys.single": path_parts})


def test_DataPath_from_spec_with_DATUM_TYPE_and_MULTI_TYPE():
    path_parts = (MapValue("a"), "b")
    assert (
        DataPath.from_spec({"path.single.map_keys": path_parts})
        == DataPath(*path_parts).single().map_keys()
    )


def test_DataPath_from_spec_with_DATUM_TYPE():
    path_parts = ("a", "b")
    assert (
        DataPath.from_spec({"path.map_keys": path_parts})
        == DataPath(*path_parts).map_keys()
    )


def test_DataPath_from_spec_with_MULTI_TYPE():
    path_parts = (MapValue("a"), "b")
    assert (
        DataPath.from_spec({"path.first": path_parts}) == DataPath(*path_parts).first()
    )
