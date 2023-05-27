import copy
import html
from pathlib import Path
import re
from typing import Any, Dict, List, Union

from ruamel.yaml import YAML
from valida.conditions import INV_DTYPE_LOOKUP, KeyDataType, ValueDataType
from valida.data import Data
from valida.datapath import Container, DataPath, ListValue, MapValue

from valida.rules import Rule


def format_map_key_value_data_type_conditions(
    cnds: List[Union[KeyDataType, ValueDataType]]
) -> str:
    out = []
    for i in cnds:
        out_i = ""
        if i.callable.name == "equal_to":
            val = i.callable.kwargs["value"]
            try:
                val = INV_DTYPE_LOOKUP[val]
            except KeyError:
                pass
            out_i += f"{val}"
        elif i.callable.name in ("is_instance", "keys_is_instance"):
            arg_concat_i = []
            for arg_j in i.callable.args:
                try:
                    arg_j = INV_DTYPE_LOOKUP[arg_j]
                except KeyError:
                    pass
                arg_concat_i.append(arg_j)
            arg_concat_i_str = " | ".join(str(i) for i in arg_concat_i)
            out_i += arg_concat_i_str
        elif i.callable.name == "in_":
            arg_concat_i = (repr(j) for j in i.callable.kwargs["value"])
            arg_concat_i_str = "(" + " | ".join(arg_concat_i) + ")"
            out_i += arg_concat_i_str
        out.append(out_i)
    if len(out) > 1:
        out_str = ", ".join(out)
    else:
        out_str = out[0]
    return out_str


def write_tree_html(tree, _path=None, anchor_root: str = None):
    empty_map_str = "map-value"
    empty_lst_str = "list-value"
    empty_map_span = (
        f'<span class="valida-tree null-condition-path-elem">[{empty_map_str}]</span>'
    )
    empty_lst_span = (
        f'<span class="valida-tree null-condition-path-elem">[{empty_lst_str}]</span>'
    )
    out = f'<div class="valida-tree node" data-node-path="{html.escape(str(_path) or "")}">'

    for child in tree:
        out += f'<div class="valida-tree node-child">'

        path_fmt_lst = []
        for i in child["path"]:
            if i == MapValue():
                i = empty_map_span
            elif i == ListValue():
                i = empty_lst_span
            else:
                i = html.escape(str(i))
            path_fmt_lst.append(str(i))
        path_fmt = " → ".join(path_fmt_lst)

        path_anchor_lst = [] if not anchor_root else [anchor_root]
        for i in child["path"]:
            if i == MapValue():
                i = empty_map_str
            elif i == ListValue():
                i = empty_lst_str
            else:
                i = html.escape(str(i))
            path_anchor_lst.append(str(i))

        path_anchor = "vld-" + "-".join(path_anchor_lst)
        path_title = " → ".join(path_anchor_lst)
        head_anchor = f"#{path_anchor}"

        out += f'<section class="valida-tree-section" id={path_anchor}>'

        if path_fmt:
            head_lev = len(child["path"]) + 1
            path_fmt_final = f"{path_fmt_lst[-1]}"  # not showing whole path?
            out += f'<div class="valida-tree path-name"><h{head_lev} title="{path_title}">{path_fmt_final}<a class="headerlink" href="{head_anchor}">#</a></h{head_lev}></div>'

        out += f'<div class="valida-tree node-info">'
        out += f'<div class="valida-tree node-metadata">'
        type_line_lst = []
        chd_type = child.get("type_fmt")
        chd_key_type = child.get("key_type_fmt")
        chd_cnd = child.get("condition")
        if chd_type:
            chd_type = str(chd_type)
            type_line_lst.append(
                f'<span class="valida-tree type-name">type: {html.escape(chd_type)}</span>'
            )
            if chd_key_type:
                chd_key_type = str(chd_key_type)
                type_line_lst[-1] += (
                    f' <span class="valida-tree key-type-name">(key: '
                    f"{html.escape(chd_key_type)})</span>"
                )

        chd_req = child.get("required")
        if _path is None:
            chd_req = True

        type_line_lst.append(
            f'<span class="valida-tree required-name">{"required" if chd_req else "optional"}</span>'
        )

        out += ", ".join(type_line_lst)

        if not chd_type and chd_cnd:
            chd_cnd = str(chd_cnd)
            out += (
                f'<div class="tree condition">Condition: {html.escape(chd_cnd)}</div>'
            )
        out += "</div>"  # node-metadata

        chd_doc = child.get("doc")
        if chd_doc:
            for doc_para in chd_doc:
                # search for back ticks and replace with `<code>` tags:
                doc_para = html.escape(doc_para)
                doc_para = re.sub(r"`(.*?)`", r"<code>\1</code>", doc_para)
                out += f'<p class="valida-tree doc">{doc_para}</p>'
        out += "</div>"  # node-info

        if "children" in child:
            out += write_tree_html(
                child["children"],
                _path=child["path"],
                anchor_root=anchor_root,
            )

        out += "</section>"
        out += "</div>"

    out += "</div>"
    return out


class Schema:
    def __init__(self, rules):
        self.rules = sorted(rules, key=lambda i: len(i.path))
        self.rule_tests = None  # Assigned by `self.validate`

    def __len__(self):
        return len(self.rules)

    def __eq__(self, other):
        if (
            type(self) == type(other)
            and self.rules == other.rules
            and self.rule_tests == other.rule_tests
        ):
            return True
        return False

    def add_schema(self, schema, root_path: DataPath):
        for rule in schema.rules:
            rule.path = root_path / rule.path
            self.rules.append(rule)

        self.rules = sorted(self.rules, key=lambda i: len(i.path))

    def to_json_like(self, *args, **kwargs):
        """Encode the rules into a JSON-compatible format.

        This does not include the `rule_tests` attribute.
        """
        out = [i.to_json_like() for i in self.rules]
        if "shared_data" in kwargs:
            return out, kwargs["shared_data"]
        else:
            return out

    @classmethod
    def from_json_like(cls, json_like, *args, **kwargs):
        """Construct from a JSON-like structure."""
        return cls(rules=[Rule.from_json_like(i) for i in json_like])

    @staticmethod
    def init_rules(rules_dat):
        rules = []
        for i in rules_dat:
            rule = Rule.from_spec(i)
            rules.append(rule)
        return rules

    @classmethod
    def from_yaml(cls, yaml_str):
        yaml = YAML(typ="safe")
        schema_dat = yaml.load(yaml_str)
        rules = cls.init_rules(schema_dat["rules"])
        return cls(rules)

    @classmethod
    def from_yaml_file(cls, path):
        yaml = YAML(
            typ="safe"
        )  # need Python-native containers e.g. for rules that check container types
        with Path(path).open("r") as fh:
            schema_dat = yaml.load(fh)
        rules = cls.init_rules(schema_dat["rules"])
        return cls(rules)

    def validate(self, data):
        if not isinstance(data, Data):
            data = Data(data)
        return ValidatedData(self, data)

    def to_tree(
        self, nested: bool = False, from_path: List = None
    ) -> List[Dict[str, Any]]:
        """Generate a more compact summary of the schema rules that can be later formatted
        in HTML, for example.

        Parameters
        ----------
        from_path
            Set the root node to a sub-node (inclusively).

        """

        IMP_TYPE_LOOKUP = {
            Container.MAP: "dict",
            Container.LIST: "list",
        }

        if from_path is None:
            from_path = []

        from_path_str = tuple(str(i) for i in from_path)
        from_path_simple = DataPath(*from_path).simplify()

        items = {}
        for rule in self.rules:
            path_simple = rule.path.simplify()
            path_str = tuple(str(i) for i in rule.path.parts)  # use as a dict key

            if path_str[: len(from_path_str)] != from_path_str:
                continue
            else:
                path_simple = path_simple[len(from_path_str) :]
                path_str = path_str[len(from_path_str) :]

            if path_str not in items:
                items[path_str] = {}

            items[path_str]["condition"] = rule.condition
            items[path_str]["path"] = path_simple
            items[path_str]["doc"] = rule.doc

            # add parent types that are implicitly defined:
            imp_types = rule.path.resolve_implicit_types()
            if imp_types:
                for idx, imp_type in enumerate(imp_types):
                    if idx == 0:
                        parent_path = []
                    else:
                        parent_path = rule.path.parts[len(from_path_str) : idx]
                    parent_path_str = tuple(str(i) for i in parent_path)

                    if parent_path_str not in items:
                        items[parent_path_str] = {}
                    items[parent_path_str]["type"] = IMP_TYPE_LOOKUP[imp_type]
                    items[parent_path_str]["type_fmt"] = items[parent_path_str]["type"]

            key_conditions = rule.condition.get_always_applicable_key_conditions()
            for key_cnd in key_conditions:
                for key in key_cnd.callable.args:
                    path_simple_i = tuple(list(path_simple) + [key])
                    path_i = rule.path[len(from_path_str) :] / DataPath(key)
                    path_i_str = tuple(str(i) for i in path_i)
                    if path_i_str not in items:
                        items[path_i_str] = {"path": path_simple_i}
                    items[path_i_str]["required"] = (
                        key_cnd.callable.name == "required_keys"
                    )

            kv_conditions = rule.condition.get_always_applicable_type_like_conditions()
            if kv_conditions["key_data_type"]:
                items[path_str]["key_type"] = kv_conditions["key_data_type"]
                items[path_str][
                    "key_type_fmt"
                ] = format_map_key_value_data_type_conditions(
                    items[path_str]["key_type"]
                )
            if kv_conditions["value_data_type"]:
                items[path_str]["type"] = kv_conditions["value_data_type"]
                items[path_str]["type_fmt"] = format_map_key_value_data_type_conditions(
                    items[path_str]["type"]
                )

        # convert to a list with parent references
        items_lst = []
        parent_refs = {tuple(): -1}
        for k, v in items.items():
            parent_path = k[:-1]
            v["parent"] = parent_refs[parent_path]
            v["path_str"] = k
            items_lst.append(v)
            parent_refs[k] = len(items_lst) - 1

        # add the final component of `from_path` back on to all paths:
        if from_path_simple:
            for item in items_lst:
                item["path"] = tuple([from_path_simple[-1]] + list(item["path"]))
                item["path_str"] = tuple([from_path_str[-1]] + list(item["path_str"]))

        if nested:
            # start popping from the end:
            parent_idx_map = sorted(
                [(idx, i["parent"]) for idx, i in enumerate(items_lst)],
                key=lambda x: (x[0], x[1]),
                reverse=True,
            )
            for lst_idx, par_idx in parent_idx_map:
                if par_idx == -1:
                    continue
                if "children" not in items_lst[par_idx]:
                    items_lst[par_idx]["children"] = []
                items_lst[par_idx]["children"].append(items_lst.pop(lst_idx))

        return items_lst


class ValidatedData:
    def __init__(self, schema, data):
        self.data = data
        self.schema = schema

        data_copy = copy.deepcopy(self.data.get_original())
        self.rule_tests = tuple(
            rule.test(self.data, _data_copy=data_copy) for rule in self.schema.rules
        )

        self.cast_data = data_copy

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"is_valid={self.is_valid!r}, "
            f"num_failures={self.num_failures}, "
            f"frac_rules_tested={self.frac_rules_tested}"
            f")"
        )

    @property
    def is_valid(self):
        return all(i.is_valid for i in self.rule_tests)

    @property
    def num_rules_tested(self):
        return sum(i.tested for i in self.rule_tests)

    @property
    def frac_rules_tested(self):
        return self.num_rules_tested / len(self.schema)

    @property
    def num_failures(self):
        return sum(i.num_failures for i in self.rule_tests)

    def get_failures_string(self):
        out = ""
        rules_tested_msg = (
            f"{self.num_rules_tested}/{len(self.schema)} rules were tested."
        )
        if self.is_valid:
            out += f"Data is valid. {rules_tested_msg}\n"
            return

        out += (
            f"{self.num_failures} rule{'s' if self.num_failures > 1 else ''} "
            f"failed validation. {rules_tested_msg}\n\n"
        )

        for rule_idx, rule_test in enumerate(self.rule_tests, start=1):
            if not rule_test.is_valid:
                rule_msg = f"Rule #{rule_idx}"
                out += rule_msg + "\n" + "-" * len(rule_msg) + "\n"
                out += rule_test.get_failures_string()
                out += "\n"

        return out

    def print_failures(self):
        print(self.get_failures_string())


class _TestDataSchema:
    def __init__(self, data, schema):
        rules = Schema.init_rules(schema["rules"])

        self.data = data
        self.schema = Schema(rules)

    @classmethod
    def from_yaml_file(cls, path):
        yaml = YAML(
            typ="safe"
        )  # need Python-native containers e.g. for rules that check container types
        with Path(path).open("r") as fh:
            all_dat = yaml.load(fh)
        test_data_schema = cls(all_dat["data"], all_dat["schema"])
        return test_data_schema

    @property
    def data_and_schema(self):
        return self.data, self.schema
