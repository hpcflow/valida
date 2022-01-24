<img src="valida.png" width="200" alt="Valida logo"/>

**Validation for nested data structures**

[![PyPI version](https://img.shields.io/pypi/v/valida "PyPI version")](https://pypi.org/project/valida)
![Testing workflow](https://github.com/hpcflow/valida/actions/workflows/test.yml/badge.svg)
[![Supported python versions](https://img.shields.io/pypi/pyversions/valida "Supported python versions")](https://pypi.org/project/valida)
[![License](https://img.shields.io/github/license/hpcflow/valida "License")](https://github.com/hpcflow/valida/blob/main/LICENSE)
[![DOI](https://zenodo.org/badge/446597552.svg)](https://zenodo.org/badge/latestdoi/446597552)

## Installing

`pip install valida`

## A simple example

```python
from valida import Data, Value, Rule

# Define some data that we want to validate:
my_data = Data({'A': 1, 'B': [1, 2, 3], 'C': {'c1': 8.2, 'c2': 'hello'}})

# Define a rule as a path within the data and a condition at that path:
rule = Rule(
  path=('C', 'c2'),
  condition=Value.dtype.equal_to(str),
)

# Test the rule
rule.test(my_data).is_valid # `True` => The rule tested successfully

```

## Acknowledgements

Valida was developed using funding from the [LightForm](https://lightform.org.uk/) EPSRC programme grant ([EP/R001715/1](https://gow.epsrc.ukri.org/NGBOViewGrant.aspx?GrantRef=EP/R001715/1))

<img src="https://lightform-group.github.io/wiki/assets/images/site/lightform-logo.png" width="150"/>

