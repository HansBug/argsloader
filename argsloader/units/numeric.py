import math
from typing import List, Tuple, Union, Mapping, Any

from .base import UncompletedUnit
from .build import CalculateUnit
from .mathop import le, lt, ge, gt
from .type import is_type


# noinspection PyPep8Naming
class _IntervalData:
    def __init__(self, intervals: List[Tuple[Union[int, float], Union[int, float], bool, bool]]):
        self._intervals = intervals

    def l(self, left) -> 'IntervalUnit':
        """
        Left-inbounded interval with positive infinite right bound, like ``(left, +inf]``.

        :param left: Left bound, which is not included.
        :return: New interval unit object which contains the new interval and all old intervals.
        """
        return IntervalUnit([*self._intervals, (left, +math.inf, False, True)])

    def L(self, left) -> 'IntervalUnit':
        """
        Left-bounded interval with positive infinite right bound, like ``[left, +inf]``.

        :param left: Left bound, which is included.
        :return: New interval unit object which contains the new interval and all old intervals.
        """
        return IntervalUnit([*self._intervals, (left, +math.inf, True, True)])

    def r(self, right) -> 'IntervalUnit':
        """
        Right-inbounded interval with negative infinite left bound, like ``[-inf, right)``.

        :param right: Right bound, which is not included.
        :return: New interval unit object which contains the new interval and all old intervals.
        """
        return IntervalUnit([*self._intervals, (-math.inf, right, True, False)])

    def R(self, right) -> 'IntervalUnit':
        """
        Right-bounded interval with negative infinite left bound, like ``[-inf, right)``.

        :param right: Right bound, which is included.
        :return: New interval unit object which contains the new interval and all old intervals.
        """
        return IntervalUnit([*self._intervals, (-math.inf, right, True, True)])

    def lr(self, left, right) -> 'IntervalUnit':
        """
        Both-side-inbounded interval, like ``(left, right)``.

        :param left: Left bound, which is not included.
        :param right: Right bound, which is not included.
        :return: New interval unit object which contains the new interval and all old intervals.
        """
        return IntervalUnit([*self._intervals, (left, right, False, False)])

    def lR(self, left, right) -> 'IntervalUnit':
        """
        Left-inbounded right-bounded interval, like ``(left, right]``.

        :param left: Left bound, which is not included.
        :param right: Right bound, which is included.
        :return: New interval unit object which contains the new interval and all old intervals.
        """
        return IntervalUnit([*self._intervals, (left, right, False, True)])

    def Lr(self, left, right) -> 'IntervalUnit':
        """
        Left-bounded right-inbounded interval, like ``[left, right)``.

        :param left: Left bound, which is included.
        :param right: Right bound, which is not included.
        :return: New interval unit object which contains the new interval and all old intervals.
        """
        return IntervalUnit([*self._intervals, (left, right, True, False)])

    def LR(self, left, right) -> 'IntervalUnit':
        """
        Both-side-bounded interval, like ``[left, right]``.

        :param left: Left bound, which is included.
        :param right: Right bound, which is included.
        :return: New interval unit object which contains the new interval and all old intervals.
        """
        return IntervalUnit([*self._intervals, (left, right, True, True)])


class _IntervalProxy(UncompletedUnit, _IntervalData):
    def _fail(self):
        raise SyntaxError('Uncompleted interval unit - as least one interval should be provided.')

    def _rinfo(self):
        return [], []


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


def _build_interval_exp(v):
    runit = None
    for int_ in v:
        l, r, il, ir = int_

        ul = ge.than(l) if il else gt.than(l)
        ur = le.than(r) if ir else lt.than(r)
        u = ul & ur
        if runit is None:
            runit = u
        else:
            runit |= u

    return runit.validity


class IntervalUnit(CalculateUnit, _IntervalData):
    """
    Overview:
        A unit for determining if a number falls within the intervals.
    """
    __names__ = ('condition',)
    __errors__ = (ValueError,)

    def __init__(self, intervals):
        """
        Constructor of class :class:`IntervalUnit`.

        :param intervals: Interval tuples.
        """
        CalculateUnit.__init__(self, _build_interval_exp(intervals))
        _IntervalData.__init__(self, intervals)

    def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
        if pres['condition']:
            return v
        else:
            raise ValueError(f'Value not in interval - '
                             f'{_interval_repr(self._intervals)} expected but {repr(v)} found.')


interval = _IntervalProxy([])
"""
Overview:
    Interval builder.
    
    For further information, see :class:`IntervalUnit`.

Intervals:
    - ``l(x)``: Left-inbounded interval with positive infinite right bound, like ``(x, +inf]``. \
        See :meth:`IntervalUnit.l`.
    - ``L(x)``: Left-bounded interval with positive infinite right bound, like ``[x, +inf]``. \
        See :meth:`IntervalUnit.L`.
    - ``r(x)``: Right-inbounded interval with negative infinite left bound, like ``[-inf, x)``. \
        See :meth:`IntervalUnit.r`.
    - ``R(x)``: Right-bounded interval with negative infinite left bound, like ``[-inf, x]``. \
        See :meth:`IntervalUnit.R`.
    - ``lr(x, y)``: Both-side-inbounded interval, like ``(x, y)``. \
        See :meth:`IntervalUnit.lr`.
    - ``Lr(x, y)``: Left-bounded right-inbounded interval, like ``[x, y)``. \
        See :meth:`IntervalUnit.Lr`.
    - ``lR(x, y)``: Left-inbounded right-bounded interval, like ``(x, y]``. \
        See :meth:`IntervalUnit.lR`.
    - ``LR(x, y)``: Both-side-bounded interval, like ``[x, y]``. \
        See :meth:`IntervalUnit.LR`.

Examples::
    >>> from argsloader.units import interval
    >>> u = interval.lR(3, 10)  # (3, 10]
    >>> u(4.5)
    4.5
    >>> u(12)
    ValueParseError: Value not in interval - (3, 10] expected but 12 found.
    >>> u(3)
    ValueParseError: Value not in interval - (3, 10] expected but 3 found.
    >>>     
    ... u = interval.lR(3, 10).L(12)  # (3, 10] | [12, +inf]
    >>> u(4.5)
    4.5
    >>> u(12)
    12
    >>> u(3)
    ValueParseError: Value not in interval - (3, 10] | [12, +inf] expected but 3 found.
"""


def positive():
    """
    Overview:
        Check if the value is positive.

        Similar to ``interval.l(0)``. See :func:`interval`.

    Examples::
        - Simple usage

        >>> from argsloader.units import positive
        >>> u = positive()
        >>> u(1)
        1
        >>> u(0.25)
        0.25
        >>> u(0)
        ValueParseError: Value not in interval - (0, +inf] expected but 0 found.

        - Positive integer

        >>> u = positive.int()
        >>> u(1)
        1
        >>> u(0.25)
        TypeParseError: Value type not match - int expected but float found.
        >>> u(0)
        ValueParseError: Value not in interval - (0, +inf] expected but 0 found.
    """
    return interval.l(0)


def _int_positive():
    return is_type(int) & positive()


positive.int = _int_positive


def negative():
    """
    Overview:
        Check if the value is negative.

        Similar to ``interval.r(0)``. See :func:`interval`.

    Examples::
        - Simple usage

        >>> from argsloader.units import negative
        >>> u = negative()
        >>> u(-1)
        -1
        >>> u(-0.25)
        -0.25
        >>> u(0)
        ValueParseError: Value not in interval - [-inf, 0) expected but 0 found.

        - Negative integer

        >>> u = negative.int()
        >>> u(-1)
        -1
        >>> u(-0.25)
        TypeParseError: Value type not match - int expected but float found.
        >>> u(0)
        ValueParseError: Value not in interval - [-inf, 0) expected but 0 found.
    """
    return interval.r(0)


def _int_negative():
    return is_type(int) & negative()


negative.int = _int_negative


def non_positive():
    """
    Overview:
        Check if the value is non-positive.

        Similar to ``interval.R(0)``. See :func:`interval`.

    Examples::
        - Simple usage

        >>> from argsloader.units import non_positive
        >>> u = non_positive()
        >>> u(-1)
        -1
        >>> u(0)
        0
        >>> u(-0.25)
        -0.25
        >>> u(1)
        ValueParseError: Value not in interval - [-inf, 0] expected but 1 found.

        - Non-positive integer

        >>> u = non_positive.int()
        >>> u(-1)
        -1
        >>> u(0)
        0
        >>> u(-0.25)
        TypeParseError: Value type not match - int expected but float found.
        >>> u(1)
        ValueParseError: Value not in interval - [-inf, 0] expected but 1 found.
    """
    return interval.R(0)


def _int_non_positive():
    return is_type(int) & non_positive()


non_positive.int = _int_non_positive


def non_negative():
    """
    Overview:
        Check if the value is non-negative.

        Similar to ``interval.L(0)``. See :func:`interval`.

    Examples::
        - Simple usage

        >>> from argsloader.units import non_negative
        >>> u = non_negative()
        >>> u(1)
        1
        >>> u(0)
        0
        >>> u(0.25)
        0.25
        >>> u(-1)
        ValueParseError: Value not in interval - [0, +inf] expected but -1 found.

        - Non-negative integer

        >>> u = non_negative.int()
        >>> u(1)
        1
        >>> u(0)
        0
        >>> u(0.25)
        TypeParseError: Value type not match - int expected but float found.
        >>> u(-1)
        ValueParseError: Value not in interval - [0, +inf] expected but -1 found.
    """
    return interval.L(0)


def _int_non_negative():
    return is_type(int) & non_negative()


non_negative.int = _int_non_negative


def nature():
    """
    Overview:
        Check if the given value is a natural number.

        The same as ``non_negative.int``, see :func:`non_negative`.

    Examples::
        >>> from argsloader.units import nature
        >>> u = nature()
        >>> u(1)
        1
        >>> u(0)
        0
        >>> u(0.25)
        TypeParseError: Value type not match - int expected but float found.
        >>> u(-1)
        ValueParseError: Value not in interval - [0, +inf] expected but -1 found.
    """
    return _int_non_negative()


class NumberUnit(CalculateUnit):
    """
    Overview:
        A unit for transform all types of number-liked data to number.
    """
    __errors__ = (ValueError, TypeError)

    def __init__(self):
        """
        Constructor of class :class:`NumberUnit`.
        """
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
    """
    Overview:
        Get a number unit, used to transform all types of number-liked data to number.

    :return: Number unit mentioned above.

    Examples::
        >>> from argsloader.units import number
        >>> u = number()
        >>> u(233)  # int
        233
        >>> u(234.5)  # float
        234.5
        >>> u('233')  # int-liked str
        233
        >>> u('234.5')  # float-liked str
        234.5
        >>> u('0x74f')  # hex-liked str
        1871
        >>> u('0o735')  # oct-liked str
        477
        >>> u('0b1010010011')  # bin-liked str
        659
        >>> u('-inf')  # neg-infinite
        -inf
        >>> u('nan')  # not a number
        nan
    """
    return _NUMBER_UNIT


class IntLikedUnit(CalculateUnit):
    """
    Overview:
        Unit for parsing int-liked number to int.
    """
    __errors__ = (ValueError,)

    def __init__(self, eps=1e-8):
        """
        Constructor of :class:`IntLikedUnit`.

        :param eps: Eps tolerance.
        """
        CalculateUnit.__init__(self)
        self.__eps = eps

    def _calculate(self, v: Union[float, int], pres: Mapping[str, Any]) -> object:
        d = int(round(v))
        if abs(d - v) < self.__eps:
            return d
        else:
            raise ValueError(f'Value expected to be an int-liked number, but {repr(v)} found.')

    def _rinfo(self):
        _, children = CalculateUnit._rinfo(self)
        return [('eps', self.__eps)], children


def int_like(eps=1e-8):
    """
    Overview:
        Check if the given value is an int-liked value.

    :param eps: Eps tolerance, default is ``1e-8``.
    :return: A unit for parsing this kind of number.

    Examples::
        >>> from argsloader.units import int_like
        >>> u = int_like()
        >>> u(233)
        233
        >>> u(233.0)
        233
        >>> u(233.002)
        ValueParseError: Value expected to be an int-liked number, but 233.002 found.
    """
    return is_type((int, float)) >> IntLikedUnit(eps)
