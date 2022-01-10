import copy
from functools import partial

import valida.callables as call_funcs
from valida.filters import FilteredMapData, FilteredListData
from valida.utils import (
    classproperty,
    make_pre_processing_mixin_class,
    null_condition_binary_check,
)


class ConditionLike:
    """Class to represent one or more testable conditions to be applied to some data."""

    def __init__(self, is_inverted=False):
        self.is_inverted = is_inverted

    def __or__(self, other):
        return Or(self, other)

    def __and__(self, other):
        return And(self, other)

    def __invert__(self):
        obj = copy.deepcopy(self)
        obj.is_inverted = not self.is_inverted
        return obj

    def __xor__(self, other):
        return Xor(self, other)

    @staticmethod
    def and_(cond_1, cond_2):
        return cond_1 & cond_2

    @staticmethod
    def or_(cond_1, cond_2):
        return cond_1 | cond_2

    @staticmethod
    def not_(cond):
        return ~cond

    @staticmethod
    def xor_(cond_1, cond_2):
        return cond_1 ^ cond_2

    def _is_like(self, cls):
        """Check a ConditionLike is either a Condition of the given superclass, or a
        combination of `BinaryOp`s that are exclusively of the given superclass."""

        if isinstance(self, BinaryOp) and issubclass(type(self.conditions[0]), cls):
            return True
        elif issubclass(type(self), cls):
            return True
        else:
            return False

    def _to_like(self, cls):

        if self._is_like(cls):
            return self

        elif not self.is_value_like:
            raise TypeError(
                "A `ConditionLike` must be value-like to be converted to being index- or "
                "key-like."
            )

        if isinstance(self, BinaryOp):
            new_binary_op = NullCondition()
            for condition_i in self.conditions:
                new_binary_op = self.__class__(
                    new_binary_op, condition_i._to_other_datum_part_condition(cls)
                )
            cnd_like = new_binary_op
        else:
            cnd_like = self._to_other_datum_part_condition(cls)

        return cnd_like

    @property
    def is_value_like(self):
        """Is the ConditionLike not all key-like or all index-like conditons?"""
        return not self.is_key_like and not self.is_index_like

    @property
    def is_key_like(self):
        return self._is_like(Key)

    @property
    def is_index_like(self):
        return self._is_like(Index)

    @property
    def is_null(self):
        return isinstance(self, NullCondition)

    def to_key_like(self):
        """Convert a value-like ConditionLike to a key-like ConditionLike."""
        return self._to_like(Key)

    def to_index_like(self):
        """Convert a value-like ConditionLike to a index-like ConditionLike."""
        return self._to_like(Index)

    def flatten(self):
        """Get a flattened list of all conditions."""
        conditions = []
        operators = []
        if isinstance(self, BinaryOp):
            for idx, condition in enumerate(self.conditions):
                if isinstance(condition, BinaryOp):
                    cnd, ops = condition.flatten()
                    conditions.extend(cnd)
                    operators.extend(ops)
                else:
                    conditions.append(condition)
                    if idx == 0:
                        operators.append(self.__class__.__name__)
        else:
            conditions.append(self)

        return conditions, operators


class Callables:
    @classmethod
    def equal_to(cls, value):
        return cls(call_funcs.equal_to, value=value)

    @classmethod
    def not_equal_to(cls, value):
        return cls(call_funcs.not_equal_to, value=value)

    @classmethod
    def less_than(cls, value):
        return cls(call_funcs.less_than, value=value)

    @classmethod
    def greater_than(cls, value):
        return cls(call_funcs.greater_than, value=value)

    @classmethod
    def less_than_or_equal_to(cls, value):
        return cls(call_funcs.less_than_or_equal_to, value=value)

    @classmethod
    def greater_than_or_equal_to(cls, value):
        return cls(call_funcs.greater_than_or_equal_to, value=value)

    @classmethod
    def in_(cls, value):
        return cls(call_funcs.in_, value=value)

    @classmethod
    def not_in(cls, value):
        return cls(call_funcs.not_in, value=value)

    @classmethod
    def in_range(cls, value):
        return cls(call_funcs.in_range, value=value)

    @classmethod
    def not_in_range(cls, value):
        return cls(call_funcs.not_in_range, value=value)

    @classmethod
    def keys_contain(cls, key):
        return cls(call_funcs.keys_contain, key=key)

    @classmethod
    def keys_contain_any_of(cls, *keys):
        return cls(call_funcs.keys_contain_any_of, keys=keys)

    @classmethod
    def keys_contain_all_of(cls, *keys):
        return cls(call_funcs.keys_contain_all_of, keys=keys)

    @classmethod
    def keys_contain_N_of(cls, N, keys):
        return cls(call_funcs.keys_contain_N_of, N=N, keys=keys)

    @classmethod
    def keys_contain_at_least_N_of(cls, N, keys):
        return cls(call_funcs.keys_contain_at_least_N_of, N=N, keys=keys)

    @classmethod
    def keys_contain_at_most_N_of(cls, N, keys):
        return cls(call_funcs.keys_contain_at_most_N_of, N=N, keys=keys)

    @classmethod
    def keys_contain_one_of(cls, keys):
        return cls(call_funcs.keys_contain_one_of, keys=keys)

    @classmethod
    def keys_contain_at_least_one_of(cls, keys):
        return cls(call_funcs.keys_contain_at_least_one_of, keys=keys)

    @classmethod
    def keys_contain_at_most_one_of(cls, keys):
        return cls(call_funcs.keys_contain_at_most_one_of, keys=keys)

    @classmethod
    def keys_equal_to(cls, *keys):
        return cls(call_funcs.keys_equal_to, keys=keys)

    @classmethod
    def items_contain(cls, **items):
        return cls(call_funcs.items_contain, **items)

    @classmethod
    def equal_to_approx(cls, value, tolerance=1e-8):
        return cls(call_funcs.equal_to_approx, value=value, tolerance=tolerance)

    @classmethod
    def truthy(cls):
        return cls(call_funcs.truthy)

    @classmethod
    def falsy(cls):
        return cls(call_funcs.falsy)

    @classmethod
    def null(cls):
        return cls(call_funcs.null)

    # Aliases for convenience:
    eq = equal_to
    lt = less_than
    gt = greater_than
    lte = less_than_or_equal_to
    gte = greater_than_or_equal_to

    OP_SYMBOL_MAP = {
        "==": equal_to,
        "<": less_than,
        ">": greater_than,
        "<=": less_than_or_equal_to,
        ">=": greater_than_or_equal_to,
    }


class Condition(ConditionLike, Callables):

    PRE_PROCESSOR = None

    def __init__(self, callable, **callable_kwargs):

        self.callable = partial(callable, **(callable_kwargs or {}))

        try:
            callable_name = self.callable.func.__name__
        except AttributeError:
            callable_name = self.callable.__name__  # if no partial arguments applied

        self.callable_name = callable_name
        self.callable_kwargs = self.callable.keywords

    def __repr__(self):

        out = f"{self.__class__.__name__}"
        out += f".{self.callable_name}"

        if len(self.callable_kwargs) == 1:
            out += f"({list(self.callable_kwargs.values())[0]!r}"
        else:
            args = [f"{k}={v!r}" for k, v in self.callable_kwargs.items()]
            out += "(" + ", ".join(args)

        out += ")"

        return out

    def __eq__(self, other):
        if type(other) is type(self) and self._members() == other._members():
            return True
        return False

    def _members(self):
        """Return data used in __eq__"""
        return (self.callable.func, self.callable_name, self.callable_kwargs)

    @classmethod
    def _from_pre_processor_class(cls, pre_processor_class):
        mixin_cls = pre_processor_class.MIXIN_CLASS
        if not issubclass(cls, mixin_cls):
            raise TypeError(
                f'Cannot combine pre-processor "{pre_processor_class.__name__}" '
                f'with "{cls.__name__}" condition.'
            )
        return make_pre_processing_mixin_class(pre_processor_class, cls)

    def test(self, datum):
        """Test if `datum` matches the condition."""
        return bool(self.callable(datum))

    def filter(self, data):
        """Return a subset of `data` that matches the condition."""
        if isinstance(data, list):
            return FilteredListData(data, [self.test(datum) for datum in data], [self])
        elif isinstance(data, dict):
            return FilteredMapData(
                data, {k: self.test(v) for k, v in data.items()}, [self]
            )


class LengthMixin:
    """Allows us to pick for which Condition classes a `.length` attribute makes sense."""

    @classproperty
    def length(cls):
        return make_pre_processing_mixin_class(Length, cls)


class DTypeMixin:
    """Allows us to pick for which Condition classes a `.dtype` attribute makes sense."""

    @classproperty
    def dtype(cls):
        return make_pre_processing_mixin_class(DType, cls)


class Length:

    MIXIN_CLASS = LengthMixin  # used to check valid Condition/pre-processor combination

    def test(self, trial_datum):
        try:
            len_dat = len(trial_datum)
        except TypeError:
            return False
        return super().test(len_dat)


class DType:

    MIXIN_CLASS = DTypeMixin  # used to check valid Condition/pre-processor combination

    def test(self, trial_datum):
        return super().test(type(trial_datum))


class Value(Condition, LengthMixin, DTypeMixin):
    def _to_other_datum_part_condition(self, cls):
        if self.PRE_PROCESSOR:
            cls = cls._from_pre_processor_class(self.PRE_PROCESSOR)
        return cls(self.callable, **self.callable_kwargs)

    def to_key(self):
        return self._to_other_datum_part_condition(Key)

    def to_index(self):
        return self._to_other_datum_part_condition(Index)


class Index(Condition):
    def filter(self, data):
        """Return a subset of `data` that matches the condition."""
        return FilteredListData(
            data, [bool(self.callable(idx)) for idx, _ in enumerate(data)], [self]
        )

    def test(self, datum):
        """Not allowed, since the index of a list item is unknown to the item itself."""
        raise NotImplementedError


class Key(Condition, LengthMixin, DTypeMixin):
    def filter(self, data):
        return FilteredMapData(data, {k: self.test(k) for k in data.keys()}, [self])


class NullCondition(Condition):
    """Class to represent a null condition that all data satisfies."""

    def __init__(self, *args, **kwargs):
        super().__init__(call_funcs.null)

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class BinaryOp(ConditionLike):
    """Class to represent the logical binary combination of two `Condition`s."""

    def __new__(cls, *conditions):
        """If one of the conditions is a NullCondition, then abort object construction,
        and just return the non-null condition."""
        return null_condition_binary_check(*conditions) or super().__new__(cls)

    def __init__(self, *conditions, is_inverted=False):

        super().__init__(is_inverted=is_inverted)

        self.conditions = conditions

        # Nonsensical to combine key-like and index-like conditions:
        flattened_conds = self.flatten()[0]
        num_key_likes = sum(i.is_key_like for i in flattened_conds)
        num_index_likes = sum(i.is_index_like for i in flattened_conds)
        if num_key_likes > 0 and num_index_likes > 0:
            raise TypeError("Cannot combine `Key` and `Index` conditions.")

    def __repr__(self):
        arg_list = [repr(i) for i in self.conditions]
        if self.is_inverted:
            arg_list.append(f"is_inverted={self.is_inverted!r}")
        out = f"{self.__class__.__name__}(" f'{", ".join(arg_list)}' f")"
        return out

    def __eq__(self, other):
        if type(self) is type(other) and (
            (
                self.conditions[0] == other.conditions[0]
                and self.conditions[1] == other.conditions[1]
            )
            or (
                self.conditions[0] == other.conditions[1]
                and self.conditions[1] == other.conditions[0]
            )
        ):
            return True
        return False

    @property
    def is_map_filterable(self):
        return self.conditions[0].is_map_filterable


class And(BinaryOp):
    """Class to represent the logical AND combination of two `ConditionLike`s."""

    def test(self, datum) -> bool:
        """Test if `datum` matches the condition."""
        return all(bool(c.test(datum)) for c in self.conditions)

    def filter(self, data):
        """Return a subset of `data` that matches the condition."""
        return self.conditions[0].filter(data) & self.conditions[1].filter(data)


class Or(BinaryOp):
    """Class to represent the logical OR combination of two `ConditionLike`s."""

    def test(self, datum) -> bool:
        """Test if `datum` matches the condition."""
        return any(bool(c.test(datum)) for c in self.conditions)

    def filter(self, data):
        """Return a subset of `data` that matches the condition."""
        return self.conditions[0].filter(data) | self.conditions[1].filter(data)


class Xor(BinaryOp):
    """Class to represent the logical XOR combination of two `ConditionLike`s."""

    def test(self, datum):
        """Test if `datum` matches the condition."""
        return sum(bool(c.test(datum)) for c in self.conditions) == 1

    def filter(self, data):
        """Return a subset of `data` that matches the condition."""
        return self.conditions[0].filter(data) ^ self.conditions[1].filter(data)
