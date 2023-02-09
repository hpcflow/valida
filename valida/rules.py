import copy
from valida.conditions import ConditionLike
from valida.casting import CAST_DTYPE_LOOKUP, CAST_LOOKUP
from valida.data import Data, set_datum
from valida.datapath import DataPath
from valida.errors import MalformedRuleSpec


class Rule:
    def __init__(self, path, condition, cast=None):

        if not isinstance(path, DataPath):
            path = DataPath(*path)

        self.path = path
        self.condition = condition
        self.cast = cast

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"path={self.path!r}, condition={self.condition!r}, cast={self.cast!r}"
            f")"
        )

    def __eq__(self, other):
        if type(other) == type(self):
            if (
                other.path == self.path
                and other.condition == self.condition
                and other.cast == self.cast
            ):
                return True
        return False

    @classmethod
    def from_spec(cls, spec):
        path = DataPath.from_part_specs(*spec["path"])
        cond = ConditionLike.from_spec(spec["condition"])
        cast = spec.get("cast")
        for cast_from in list((cast or {}).keys()):

            cast_to = cast.pop(cast_from)
            try:
                cast_from = CAST_DTYPE_LOOKUP[cast_from]
            except KeyError:
                raise MalformedRuleSpec(f"Unknown cast_from type: {cast_from!r}")

            try:
                cast_to = CAST_DTYPE_LOOKUP[cast_to]
            except KeyError:
                raise MalformedRuleSpec(f"Unknown cast_to type: {cast_to!r}")

            try:
                cast[cast_from] = CAST_LOOKUP[(cast_from, cast_to)]
            except KeyError:
                raise MalformedRuleSpec(
                    f"Unsupported cast from type {cast_from!r} to type {cast_to!r}."
                )

        return cls(path=path, condition=cond, cast=cast)

    @classmethod
    def from_json_like(cls, json_like, *args, **kwargs):
        return cls.from_spec(json_like)

    def to_json_like(self, *args, **kwargs):
        out = {
            "condition": self.condition.to_json_like(),
            "cast": self.cast,
            "path": self.path.to_json_like(),
        }
        if "shared_data" in kwargs:
            return out, kwargs["shared_data"]
        else:
            return out

    def test(self, data, _data_copy=None):

        if not isinstance(data, Data):
            data = Data(data)

        if not self.cast:
            data_copy = data
        else:
            data_copy = _data_copy or copy.deepcopy(data.get_original())
            sub_data = self.path.get_data(data, return_paths=True)
            path_exists = sub_data not in [None, []]
            if self.path.is_concrete:
                sub_data = [sub_data]
            if path_exists:
                for datum, datum_path in sub_data:
                    for k, v in self.cast.items():
                        if isinstance(datum, k):
                            try:
                                datum = v(datum)
                                break
                            except TypeError:
                                pass
                    datum_path = DataPath(*datum_path)
                    set_datum(data_copy, datum_path, datum)

        return RuleTest(self, data_copy)


class RuleTestFailureItem:
    def __init__(self, rule_test, index, value, path, reasons):

        self.rule_test = rule_test
        self.index = index
        self.value = value
        self.path = path
        self.reasons = reasons

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"value={self.value!r}, path={self.path!r}), reasons={self.reasons!r}"
            f")"
        )


class RuleTest:
    def __init__(self, rule, data):

        if not isinstance(data, Data):
            data = Data(data)

        self.rule = rule
        self.data = data

        self._tested = False  # assigned by `_test()` - True if the rule path existed
        self._is_valid = None  # assigned by `_test()`
        self._failures = None  # assigned by `_test()`

        self._test()

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"is_valid={self.is_valid!r}, num_failures={self.num_failures!r}"
            f")"
        )

    def __eq__(self, other):
        if type(other) == type(self):
            if other.rule == self.rule and other.data is self.data:
                return True
        return False

    @property
    def is_valid(self):
        return self._is_valid

    @property
    def tested(self):
        return self._tested

    @property
    def num_failures(self):
        return len(self.failures)

    @property
    def failures(self):
        return self._failures

    def get_failures_string(self):
        out = ""
        if not self.failures:
            out += "Rule test is valid.\n"
        for fail in self.failures:
            out += f"Path: {fail.path!r}\nValue: {fail.value!r}\nReasons:\n"
            for reason in fail.reasons:
                out += " " + reason + "\n"
        return out

    def print_failures(self):
        print(self.get_failures_string())

    def _test(self):

        sub_data = self.rule.path.get_data(self.data, return_paths=True)
        path_exists = sub_data not in [None, []]

        if self.rule.path.is_concrete:
            sub_data = [sub_data]

        self.sub_data = sub_data

        failures = []
        if path_exists:
            filtered_data = self.rule.condition.filter(
                sub_data,
                data_has_paths=True,
                source_data=self.data,
            )
            if all(filtered_data.result):
                self._is_valid = True

            else:
                self._is_valid = False
                for f_item in filtered_data:
                    if not f_item.result:
                        failure_item = RuleTestFailureItem(
                            rule_test=self,
                            index=f_item.index,
                            value=f_item.source,
                            path=f_item.concrete_path,
                            reasons=f_item.get_failure(),
                        )
                        failures.append(failure_item)

            self.filter = filtered_data
            self._tested = True

        else:
            self._is_valid = True
            self._tested = False
            self.filter = None

        self._failures = tuple(failures)
