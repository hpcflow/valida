from textwrap import dedent

import pytest

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
