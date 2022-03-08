import re
from typing import Mapping, Any

from hbutils.string import env_template, truncate

from .base import CalculateUnit, _to_unit, UncompletedUnit

try:
    from re import Pattern
except ImportError:
    Pattern = type(re.compile(''))


class TemplateUnit(CalculateUnit):
    __names__ = ('tmp', 'vars', 'safe')
    __errors__ = (KeyError,)

    def __init__(self, tmp, variables: Mapping[str, Any], safe):
        CalculateUnit.__init__(self, tmp, {k: _to_unit(v) for k, v in variables.items()}, safe)

    def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
        # print(pres)
        return env_template(pres['tmp'], pres['vars'], safe=pres['safe'])


def template(tmp, vars_, safe: bool = False) -> TemplateUnit:
    return TemplateUnit(tmp, vars_, safe)


class RegexpMatchUnit(CalculateUnit):
    __names__ = ('regexp',)
    __errors__ = (ValueError,)

    def __init__(self, r, fullmatch: bool = False, check_only: bool = False):
        self._regexp = r
        self._fullmatch = fullmatch
        self._check_only = check_only
        CalculateUnit.__init__(self, r)

    @property
    def full(self) -> 'RegexpMatchUnit':
        return self.__class__(self._regexp, True, self._check_only)

    @property
    def check(self) -> 'RegexpMatchUnit':
        return self.__class__(self._regexp, self._fullmatch, True)

    def _calculate(self, v: str, pres: Mapping[str, Any]):
        r = pres['regexp']
        if not isinstance(r, Pattern):
            r = re.compile(r)

        mfunc = r.fullmatch if self._fullmatch else r.match
        match = mfunc(v)
        if match:
            if self._check_only:
                return v
            else:
                return {
                    0: match.group(0),
                    **{i + 1: content for i, content in enumerate(match.groups())},
                    **match.groupdict(),
                }
        else:
            raise ValueError(f'Regular expression {repr(r.pattern)} expected, '
                             f'but {truncate(repr(v))} found which is '
                             f'not {"fully " if self._fullmatch else ""}matched.')

    def _rinfo(self):
        _, children = super()._rinfo()
        return [
                   ('fullmatch', self._fullmatch),
                   ('check_only', self._check_only),
               ], children


class RegexpProxy(UncompletedUnit):
    def __init__(self, r) -> None:
        UncompletedUnit.__init__(self)
        self._regexp = r

    def _fail(self):
        raise SyntaxError('Uncompleted regular expression unit - no command is given.')

    def _rinfo(self):
        return [], []

    @property
    def match(self):
        return RegexpMatchUnit(self._regexp, False, False)


def regexp(r) -> RegexpProxy:
    return RegexpProxy(r)
