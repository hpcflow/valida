
<a name="v0.7.3"></a>
## [v0.7.3](https://github.com/hpcflow/valida/compare/v0.7.2...v0.7.3) - 2024.11.14

### 🐛 Bug Fixes

* use checkout token
* bump a checkout GHA
* use hpcflow-actions user in release workflow
* bump GHA versions
* bump deps


<a name="v0.7.2"></a>
## [v0.7.2](https://github.com/hpcflow/valida/compare/v0.7.1...v0.7.2) - 2023.08.17

### 🐛 Bug Fixes

* Schema.to_tree


<a name="v0.7.1"></a>
## [v0.7.1](https://github.com/hpcflow/valida/compare/v0.7.0...v0.7.1) - 2023.07.03

### 🐛 Bug Fixes

* bumps python version upper bound to <4.0.0

### 👷 Build changes

* bumps python version upper bound to <4.0.0


<a name="v0.7.0"></a>
## [v0.7.0](https://github.com/hpcflow/valida/compare/v0.6.0...v0.7.0) - 2023.05.28

### ✨ Features

* refinements to Schema.to_tree and write_tree_html

### 🐛 Bug Fixes

* incorrect implicit parent type when to_tree from_path specified


<a name="v0.6.0"></a>
## [v0.6.0](https://github.com/hpcflow/valida/compare/v0.5.2...v0.6.0) - 2023.05.26

### ♻ Code Refactoring

* rename write_tree_template -> write_tree_html
* use more specific html class names in write_tree_template
* whitespace
* whitespace

### ✨ Features

* add from/to_json_like to Schema
* add arg anchor_root to write_tree_html
* add rule docs to Schema.to_tree and write_tree_html outputs
* add doc attribute to Rule for documenting it.
* add arg from_path to Schema.to_tree
* add Schema.to_tree and .write_tree_template
* add Schema.add_schema()
* add DataPath.simplify
* add callable keys_is_instance
* sort rules by path length on Schema init

### 🐛 Bug Fixes

* missing import
* Condition.to_json_like in the general case
* Schema to_tree
* add missing import in test
* add to_json_like method to ConditionBinaryOp
* DataPath.to_part_specs for ContainerValue objects


<a name="v0.5.2"></a>
## [v0.5.2](https://github.com/hpcflow/valida/compare/v0.5.1...v0.5.2) - 2023.04.25

### 🐛 Bug Fixes

* remove unused imports (bad IDE auto-imports?)


<a name="v0.5.1"></a>
## [v0.5.1](https://github.com/hpcflow/valida/compare/v0.5.0...v0.5.1) - 2023.04.05

### 🐛 Bug Fixes

* poetry python dep


<a name="v0.5.0"></a>
## [v0.5.0](https://github.com/hpcflow/valida/compare/v0.4.0...v0.5.0) - 2023.02.09

### ✨ Features

* add to/from_json_like methods to Condition, DataPath, Rule


<a name="v0.4.0"></a>
## [v0.4.0](https://github.com/hpcflow/valida/compare/v0.3.0...v0.4.0) - 2022.03.29

### ✨ Features

* first attempt at casting support


<a name="v0.3.0"></a>
## [v0.3.0](https://github.com/hpcflow/valida/compare/v0.2.2...v0.3.0) - 2022.03.29

### ✨ Features

* add is_instance callable, norm dtype case


<a name="v0.2.2"></a>
## [v0.2.2](https://github.com/hpcflow/valida/compare/v0.2.1...v0.2.2) - 2022.03.28

### 🐛 Bug Fixes

* add bool dtype to ConditionLike.fromspec

### 👷 Build changes

* update deps


<a name="v0.2.1"></a>
## [v0.2.1](https://github.com/hpcflow/valida/compare/v0.2.0...v0.2.1) - 2022.03.24

### ♻ Code Refactoring

* add get_failure_strings

### 🐛 Bug Fixes

* use yaml safe loader in `Schema.from_yaml` to ensure loaded types are native
* YAML parsing of condition "value.type.in: [...]"
* `MapValue` (`ListValue`) filter list (dict) now raises TypeError

### 👷 Build changes

* add DOI from zenodo
* update author email
* add readme property in pyproject.toml


<a name="v0.2.0"></a>
## [v0.2.0](https://github.com/hpcflow/valida/compare/v0.1.1...v0.2.0) - 2022.01.24

### ♻ Code Refactoring

* remove use of dynamically generated classes

### ✨ Features

* add some top-level imports for easier access
* flesh out and complete currenty required feature set

### 🐛 Bug Fixes

* remove unused module

### 👷 Build changes

* update release workflow to publish to pypi
* update gitignore


<a name="v0.1.1"></a>
## [v0.1.1](https://github.com/hpcflow/valida/compare/v0.1.0...v0.1.1) - 2022.01.11

### 🐛 Bug Fixes

* add return type to a callable

### 👷 Build changes

* update changelog
* add GH action workflows, changelog config, pre-commit config


<a name="v0.1.0"></a>
## v0.1.0 - 2022.01.10

### ✨ Features

* initial commit

