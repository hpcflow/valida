import pytest

from valida.utils import get_func_args_by_kind


def test_func_args_by_kind_func1():
    def functest1(a, c=1):
        return {
            "POSITIONAL_OR_KEYWORD": ["a", "c"],
            "VAR_POSITIONAL": [],
            "VAR_KEYWORD": [],
        }

    assert get_func_args_by_kind(functest1) == functest1(1)


def test_func_args_by_kind_func2():
    def functest2(a, c=1, **kwargs):
        return {
            "POSITIONAL_OR_KEYWORD": ["a", "c"],
            "VAR_POSITIONAL": [],
            "VAR_KEYWORD": ["kwargs"],
        }

    assert get_func_args_by_kind(functest2) == functest2(1)


def test_func_args_by_kind_func3():
    def functest3(a, c=1, **d):
        return {
            "POSITIONAL_OR_KEYWORD": ["a", "c"],
            "VAR_POSITIONAL": [],
            "VAR_KEYWORD": ["d"],
        }

    assert get_func_args_by_kind(functest3) == functest3(1)


def test_func_args_by_kind_func4():
    def functest4(a, c=1, *d, **kwargs):
        return {
            "POSITIONAL_OR_KEYWORD": ["a", "c"],
            "VAR_POSITIONAL": ["d"],
            "VAR_KEYWORD": ["kwargs"],
        }

    assert get_func_args_by_kind(functest4) == functest4(1)
