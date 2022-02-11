from textwrap import dedent

import pytest
from valida.data import Data

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
