import pytest

from valida.conditions import Value, Key, Index
from valida.data import Data


@pytest.fixture
def list_data_expected_truth_tables():
    c1a = Value.lt(2)
    c1b = Value.gt(2)
    c1c = Value.eq(3)

    c2a = c1a & c1b
    c2b = c1a | c1b
    c2c = c1a ^ c1b

    c3a = c1a & c1b | c1c  # `&` takes precedence over `|`
    c3b = c1a | c1b & c1c  # `&` takes precedence over `|`
    c3c = c1a & (c1b | c1c)  # parentheses to take precedence over `&`

    tt1a = ("Value.less_than(value=2)", [True, False, False, False])
    tt1b = ("Value.greater_than(value=2)", [False, False, True, True])
    tt1c = ("Value.equal_to(value=3)", [False, False, True, False])

    b_tta = [tt1a, tt1b, ("and", [False, False, False, False])]
    b_ttb = [tt1a, tt1b, ("or", [True, False, True, True])]
    b_ttc = [tt1a, tt1b, ("xor", [True, False, True, True])]

    out = {
        "data": [1, 2, 3, 4],
        "conditions": (c1a, c1b, c1c),
        "binary_conditions": (c2a, c2b, c2c),
        "ternary_conditions": (c3a, c3b, c3c),
        "truth_tables": ([tt1a], [tt1b], [tt1c]),
        "binary_truth_tables": (b_tta, b_ttb, b_ttc),
        "ternary_truth_tables": (
            [
                tt1a,
                tt1b,
                ("and", [False, False, False, False]),
                tt1c,
                ("or", [False, False, True, False]),
            ],
            [
                tt1a,
                tt1b,
                tt1c,
                ("and", [False, False, True, False]),
                ("or", [True, False, True, False]),
            ],
            [
                tt1a,
                tt1b,
                tt1c,
                ("or", [False, False, True, True]),
                ("and", [False, False, False, False]),
            ],
        ),
    }
    return out


@pytest.fixture
def list_data_actual_truth_tables(list_data_expected_truth_tables):
    c1a = list_data_expected_truth_tables["conditions"][0]
    c1b = list_data_expected_truth_tables["conditions"][1]
    c1c = list_data_expected_truth_tables["conditions"][2]

    c2a = list_data_expected_truth_tables["binary_conditions"][0]
    c2b = list_data_expected_truth_tables["binary_conditions"][1]
    c2c = list_data_expected_truth_tables["binary_conditions"][2]

    c3a = list_data_expected_truth_tables["ternary_conditions"][0]
    c3b = list_data_expected_truth_tables["ternary_conditions"][1]
    c3c = list_data_expected_truth_tables["ternary_conditions"][2]

    data = list_data_expected_truth_tables["data"]

    return {
        "truth_tables": (
            c1a.filter(data).truth_table,
            c1b.filter(data).truth_table,
            c1c.filter(data).truth_table,
        ),
        "binary_truth_tables": (
            c2a.filter(data).truth_table,
            c2b.filter(data).truth_table,
            c2c.filter(data).truth_table,
        ),
        "ternary_truth_tables": (
            c3a.filter(data).truth_table,
            c3b.filter(data).truth_table,
            c3c.filter(data).truth_table,
        ),
    }


def test_filter_truth_tables(
    list_data_expected_truth_tables, list_data_actual_truth_tables
):
    assert (
        list_data_expected_truth_tables["truth_tables"][0]
        == list_data_actual_truth_tables["truth_tables"][0]
    )
    assert (
        list_data_expected_truth_tables["truth_tables"][1]
        == list_data_actual_truth_tables["truth_tables"][1]
    )
    assert (
        list_data_expected_truth_tables["truth_tables"][2]
        == list_data_actual_truth_tables["truth_tables"][2]
    )


def test_binary_op_filter_truth_tables(
    list_data_expected_truth_tables, list_data_actual_truth_tables
):
    assert (
        list_data_expected_truth_tables["binary_truth_tables"][0]
        == list_data_actual_truth_tables["binary_truth_tables"][0]
    )

    assert (
        list_data_expected_truth_tables["binary_truth_tables"][1]
        == list_data_actual_truth_tables["binary_truth_tables"][1]
    )

    assert (
        list_data_expected_truth_tables["binary_truth_tables"][2]
        == list_data_actual_truth_tables["binary_truth_tables"][2]
    )


def test_ternary_op_filter_truth_tables(
    list_data_expected_truth_tables, list_data_actual_truth_tables
):
    assert (
        list_data_expected_truth_tables["ternary_truth_tables"][0]
        == list_data_actual_truth_tables["ternary_truth_tables"][0]
    )

    assert (
        list_data_expected_truth_tables["ternary_truth_tables"][1]
        == list_data_actual_truth_tables["ternary_truth_tables"][1]
    )

    assert (
        list_data_expected_truth_tables["ternary_truth_tables"][2]
        == list_data_actual_truth_tables["ternary_truth_tables"][2]
    )


def test_equivalence_of_data_filter_condition_and_condition_filter_data():
    my_data = Data([1, 2, 3])
    condition = Value.eq(2)
    assert my_data.filter(condition).data == condition.filter(my_data).data


def test_coercion_to_data_obj_in_condition_filter():
    dat_1 = [1, 2, 3]
    dat_2 = Data(dat_1)
    condition = Value.eq(2)
    assert condition.filter(dat_1) == condition.filter(dat_2)


def test_equivalence_of_filter_with_data_has_paths():
    data = [7, 8, 9]
    data_with_paths = [(i, idx) for idx, i in enumerate(data)]
    condition = Value.eq(8)
    f1 = condition.filter(data, data_has_paths=False)
    f2 = condition.filter(data_with_paths, data_has_paths=True)

    assert f1.source == f2.source and f1.data == f2.data
