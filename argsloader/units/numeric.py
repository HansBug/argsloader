import math
from typing import List, Tuple, Union, Mapping, Any

from .base import UncompletedUnit, CalculateUnit
from .mathop import le, lt, ge, gt
from .utils import validate, keep


# noinspection PyPep8Naming
class _IntervalData:
    def __init__(self, intervals: List[Tuple[Union[int, float], Union[int, float], bool, bool]]):
        self._intervals = intervals

    def l(self, left) -> 'IntervalUnit':
        return IntervalUnit([*self._intervals, (left, +math.inf, False, True)])

    def L(self, left) -> 'IntervalUnit':
        return IntervalUnit([*self._intervals, (left, +math.inf, True, True)])

    def r(self, right) -> 'IntervalUnit':
        return IntervalUnit([*self._intervals, (-math.inf, right, True, False)])

    def R(self, right) -> 'IntervalUnit':
        return IntervalUnit([*self._intervals, (-math.inf, right, True, True)])

    def lr(self, left, right) -> 'IntervalUnit':
        return IntervalUnit([*self._intervals, (left, right, False, False)])

    def lR(self, left, right) -> 'IntervalUnit':
        return IntervalUnit([*self._intervals, (left, right, False, True)])

    def Lr(self, left, right) -> 'IntervalUnit':
        return IntervalUnit([*self._intervals, (left, right, True, False)])

    def LR(self, left, right) -> 'IntervalUnit':
        return IntervalUnit([*self._intervals, (left, right, True, True)])


class _IntervalProxy(UncompletedUnit, _IntervalData):
    def _fail(self):
        raise SyntaxError('Uncompleted interval unit - as least one interval should be provided.')


def _interval_val(v):
    if math.isinf(v):
        return '+inf' if v > 0 else '-inf'
    elif isinstance(v, float):
        return '%.4f' % (v,)
    else:
        return str(v)


def _interval_repr(v):
    return ' | '.join([
        f'{"[" if il else "("}{_interval_val(l)}, {_interval_val(r)}{"]" if ir else ")"}'
        for l, r, il, ir in v
    ])


class _IntervalValueError(Exception):
    pass


def _build_interval_exp(v):
    runit = None
    for int_ in v:
        l, r, il, ir = int_

        ul = validate(keep(), ge.by(l) if il else gt.by(l), _IntervalValueError, '')
        ur = validate(keep(), le.by(r) if ir else lt.by(r), _IntervalValueError, '')
        u = ul & ur
        if runit is None:
            runit = u
        else:
            runit |= u

    return runit.validity


class IntervalUnit(CalculateUnit, _IntervalData):
    __names__ = ('condition',)
    __errors__ = (ValueError,)

    def __init__(self, intervals):
        CalculateUnit.__init__(self, _build_interval_exp(intervals))
        _IntervalData.__init__(self, intervals)

    def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
        if pres['condition']:
            return v
        else:
            raise ValueError(f'Value not in interval - '
                             f'{_interval_repr(self._intervals)} expected but {repr(v)} found.')


interval = _IntervalProxy([])


class NumberUnit(CalculateUnit):
    __errors__ = (ValueError, TypeError)

    def __init__(self):
        CalculateUnit.__init__(self)

    def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
        if isinstance(v, (int, float)):
            return v
        elif isinstance(v, str):
            try:
                if v.lower().startswith('0x'):
                    return int(v, 16)
                elif v.lower().startswith('0o'):
                    return int(v, 8)
                elif v.lower().startswith('0b'):
                    return int(v, 2)
                else:
                    try:
                        return int(v)
                    except ValueError:
                        return float(v)
            except ValueError:
                raise ValueError(f'Unrecognized value format - {repr(v)}.')

        else:
            raise TypeError(f'Value type not match - int, float or str expected but {type(v).__name__} found.')


_NUMBER_UNIT = NumberUnit()


def number() -> NumberUnit:
    return _NUMBER_UNIT
