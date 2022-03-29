from textwrap import dedent

from valida.casting import cast_string_to_bool
from valida.schema import Schema
from valida.rules import Rule
from valida.conditions import Value, NullCondition


def test_expected_return_from_yaml_1():
    yaml_str = dedent(
        r"""
        rules:
          - path: [a, b, c]
            condition: {value.equal_to: 1}
    """
    )
    schema = Schema.from_yaml(yaml_str)
    assert schema == (
        Schema(rules=[Rule(path=["a", "b", "c"], condition=Value.equal_to(1))])
    )


def test_expected_return_from_yaml_null_condition():
    yaml_str = dedent(
        r"""
        rules:
          - path: [a, b, c]
            condition: null
    """
    )
    schema = Schema.from_yaml(yaml_str)
    assert schema == (
        Schema(rules=[Rule(path=["a", "b", "c"], condition=NullCondition())])
    )


def test_expected_return_dtype_in():
    yaml_str = dedent(
        r"""
        rules:
          - path: [A]
            condition:
              value.type.in: [list, dict]
        """
    )
    schema_from_yaml = Schema.from_yaml(yaml_str)
    schema = Schema(rules=[Rule(path=["A"], condition=Value.dtype.in_([list, dict]))])
    assert schema_from_yaml == schema


def test_cast_str_to_bool():
    r = Rule(
        path=["telemetry"],
        condition=Value.dtype.equal_to(bool),
        cast={str: cast_string_to_bool},
    )
    schema = Schema(rules=[r])
    data = {"telemetry": "true"}
    validated_data = schema.validate(data)
    assert validated_data.is_valid and validated_data.cast_data == {"telemetry": True}


def test_cast_str_to_bool_and_str_to_int():
    schema = Schema(
        rules=[
            Rule(
                path=["A"],
                condition=Value.dtype.equal_to(bool),
                cast={str: cast_string_to_bool},
            ),
            Rule(
                path=["B"],
                condition=Value.equal_to(3),
                cast={str: int},
            ),
        ]
    )

    data = {"A": "true", "B": "3"}
    cast_data = {"A": True, "B": 3}
    validated_data = schema.validate(data)
    assert validated_data.is_valid and validated_data.cast_data == cast_data
