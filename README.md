# argsloader

[![PyPI](https://img.shields.io/pypi/v/argsloader)](https://pypi.org/project/argsloader/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/argsloader)](https://pypi.org/project/argsloader/)
![Loc](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/HansBug/71f7be2801b7777b3708a0bc278d43c2/raw/loc.json)
![Comments](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/HansBug/71f7be2801b7777b3708a0bc278d43c2/raw/comments.json)

[![Docs Deploy](https://github.com/HansBug/argsloader/workflows/Docs%20Deploy/badge.svg)](https://github.com/HansBug/argsloader/actions?query=workflow%3A%22Docs+Deploy%22)
[![Code Test](https://github.com/HansBug/argsloader/workflows/Code%20Test/badge.svg)](https://github.com/HansBug/argsloader/actions?query=workflow%3A%22Code+Test%22)
[![Badge Creation](https://github.com/HansBug/argsloader/workflows/Badge%20Creation/badge.svg)](https://github.com/HansBug/argsloader/actions?query=workflow%3A%22Badge+Creation%22)
[![Package Release](https://github.com/HansBug/argsloader/workflows/Package%20Release/badge.svg)](https://github.com/HansBug/argsloader/actions?query=workflow%3A%22Package+Release%22)
[![codecov](https://codecov.io/gh/HansBug/argsloader/branch/main/graph/badge.svg?token=XJVDP4EFAT)](https://codecov.io/gh/HansBug/argsloader)

[![GitHub stars](https://img.shields.io/github/stars/HansBug/argsloader)](https://github.com/HansBug/argsloader/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/HansBug/argsloader)](https://github.com/HansBug/argsloader/network)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/HansBug/argsloader)
[![GitHub issues](https://img.shields.io/github/issues/HansBug/argsloader)](https://github.com/HansBug/argsloader/issues)
[![GitHub pulls](https://img.shields.io/github/issues-pr/HansBug/argsloader)](https://github.com/HansBug/argsloader/pulls)
[![Contributors](https://img.shields.io/github/contributors/HansBug/argsloader)](https://github.com/HansBug/argsloader/graphs/contributors)
[![GitHub license](https://img.shields.io/github/license/HansBug/argsloader)](https://github.com/HansBug/argsloader/blob/master/LICENSE)

Configuration Parsing and Management Based on [chainloader](https://github.com/HansBug/chainloader).


## Installation

You can simply install it with `pip` command line from the official PyPI site.

```shell
pip install argsloader
```

For more information about installation, you can refer to [Installation](https://HansBug.github.io/argsloader/main/tutorials/installation/index.html).

## Quick Start

### Painless Try

A simple usage is like above

```python
from argsloader.units import yesno, number, is_type, interval

if __name__ == '__main__':
    yn = yesno()  # yes-no option
    print(yn('yes'))  # True
    print(yn('no'))  # False
    print(yn(True))  # True
    print(yn(False))  # False

    num = number()  # any number
    print(num(1))  # 1
    print(num('1.2'))  # 1.2
    print(num('0x4f'))  # 79

    int_ = number() >> is_type(int)  # any int number
    print(num(1))  # 1
    print(num('0x4f'))  # 79
    print(num(1.2))  # TypeError

    val_ = number() >> interval.LR(0, 10)  # number within [0, 10]
    print(num(1))  # 1
    print(num(1.2))  # 1.2
    print(num(11))  # ValueError

```

After the unit is built, it can be used to transform and validate the given value.

### Full Validation

Sometimes, there may be multiple errors in the given value, you can use method `call` to show them all.

```python
from argsloader.units import is_type, interval

if __name__ == '__main__':
    in_ = is_type(int) & interval.LR(0, 10)  # int within [0, 10]
    print(in_.call(1))  # OK
    print(in_.call(10))  # OK
    print(in_.call(11.2))  # not an int, not in [0, 10] neither

```

The output should be

```
1
10
Traceback (most recent call last):
  File "test_main.py", line 7, in <module>
    print(in_.call(11.2))
  File "/home/hansbug/sensetime-projects/argsloader/argsloader/units/base.py", line 249, in call
    return self._process(PValue(v, ())).act(err_mode)
  File "/home/hansbug/sensetime-projects/argsloader/argsloader/base/result.py", line 268, in act
    raise self._full_error()
argsloader.base.exception.MultipleParseError: (2 errors)
  <root>: TypeParseError: Value type not match - int expected but float found.
  <root>: ValueParseError: Value not in interval - [0, 10] expected but 11.2 found.
```



## Contributing

We appreciate all contributions to improve `argsloader`, both logic and system designs. Please refer to CONTRIBUTING.md for more guides.

## License

`argsloader` released under the Apache 2.0 license.

