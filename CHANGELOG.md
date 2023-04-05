
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

