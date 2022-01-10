from containers import (
    Container,
    ContainerPath,
    ListItem,
    DictValue,
    AmbiguousItem,    
)
from errors import IncompatibleRules, DuplicateRule

def parse_string_path(path):
    
    LIST_ITEM_PLACEHOLDER = '<<li>>'
    DICT_VALUE_PLACEHOLDER = '<<dv>>'

    path_out = ContainerPath()
    for i in path:
        
        if isinstance(i, str):
            if i == LIST_ITEM_PLACEHOLDER:
                i = ListItem()
            elif i == DICT_VALUE_PLACEHOLDER:
                i = DictValue()
            else:
                i = DictValue(i)
        elif isinstance(i, float):
            i = DictValue(i)
        elif isinstance(i, int):
            i = AmbiguousItem(i)

        path_out = path_out / i

    return path_out

def resolve_implicit_types(path):
    
    types = []
    for i in path:
        
        # Note: we don't support "complex mappings" from YAML where keys are themselves
        # mappings or lists

        # print(f'type i: {type(i)}')
        
        if isinstance(i, ListItem):
            type_i = Container.LIST

        elif isinstance(i, DictValue):
            type_i = Container.DICT
        
        elif isinstance(i, AmbiguousItem):
            type_i = Container.CONTAINER

        else:
            raise TypeError(f'Unknown container item type: "{type(i)}"')

        types.append(type_i)

    return types

def validate_rule_paths(rules):

    seen_paths = []
    predicted_types = {}
    for r_idx, r in enumerate(rules):
        r_path = r['path']
        if r_path in seen_paths:
            msg = f'Rule index {r_idx} shares with another rule the path: {r_path}'
            raise DuplicateRule(msg)
        else:
            seen_paths.append(r_path)
            # print(f'r_path: {r_path!r} is not in seen_paths:\n{seen_paths!r}\n')
        r_types = resolve_implicit_types(r_path)
        
        
        # print(f'predicted_types: {predicted_types}')
        
        for path_end_idx in range(len(r_path)):
            partial_path = r_path[0:path_end_idx]
            partial_path_str = f'{partial_path!r}'
            # print(path_end_idx, partial_path)
            if partial_path_str in predicted_types:
                predicted_types[partial_path_str]['rules'].append(r_idx)
                predicted_types[partial_path_str]['types'].append(r_types[path_end_idx])
            else:
                predicted_types[partial_path_str] = {
                    'rules': [r_idx],
                    'types': [r_types[path_end_idx]]
                }

    # Identify type, where possible, for each node
    for path, types_info in predicted_types.items():
        
        uniq_types = set(types_info['types'])
        
        if len(uniq_types) == 1:
            actual_type = list(uniq_types)[0]
        
        elif Container.LIST in uniq_types and Container.DICT in uniq_types:
            path_rules = [(i, rules[i]['path']) for i in types_info['rules']]
            # print(path_rules)
            path_rules_fmt = '\n\t' + '\n\t'.join(
                f'Rule index {i[0]}: {i[1]!r}' for i in path_rules)
            msg = (f'Incompatible rules specified for path {path}; at least one rule '
                   f'implies this node is a mapping, but at least one other rule implies '
                   f'this node is a list. Associated rule paths are: {path_rules_fmt}')
            raise IncompatibleRules(msg)
        
        elif Container.CONTAINER in uniq_types:

            if Container.LIST in uniq_types:
                actual_type = Container.LIST
            
            elif Container.DICT in uniq_types:
                actual_type = Container.DICT
        
        else:
            raise RuntimeError('Unique container types not understood.')

        predicted_types[path] = actual_type

    return predicted_types
