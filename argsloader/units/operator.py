from typing import Tuple, Iterator

from .base import BaseUnit, UnitProcessProxy, _to_unit
from ..base import ParseResult, PValue


class _IChainUnit(BaseUnit):
    def __init__(self, unit: BaseUnit, *units: BaseUnit):
        self._units: Tuple[BaseUnit, ...] = tuple(map(_to_unit, (unit, *units)))

    def _rinfo(self):
        return [('count', len(self._units))], [(i, u) for i, u in enumerate(self._units)]

    def _easy_process(self, v: PValue, proxy: UnitProcessProxy) -> ParseResult:
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def _chain_iter(cls, *units) -> Iterator[BaseUnit]:
        if units:
            if isinstance(units[0], cls):
                yield from cls._chain_iter(*units[0]._units)
            else:
                yield units[0]

            for unit in units[1:]:
                yield unit


class PipeUnit(_IChainUnit):
    """
    Overview:
        Unit for pipe all the units together.
    """

    def __init__(self, *units: BaseUnit):
        """
        Constructor of :class:`PipeUnit`.

        :param units: Unit to be piped together.
        """
        _IChainUnit.__init__(self, *units)

    def _easy_process(self, v: PValue, proxy: UnitProcessProxy) -> ParseResult:
        curv, rs, valid = v, [], True
        for i, unit in enumerate(self._units):
            if valid:
                curres = unit._process(curv)
                rs.append(curres)
                if not curres.status.valid:
                    valid = False
                else:
                    curv = curres.result
            else:
                rs.append(unit._skip(v))

        if valid:
            return proxy.success(curv, rs)
        else:
            return proxy.error(None, rs)


# noinspection PyProtectedMember
def _cpipe(*units) -> PipeUnit:
    """
    Overview:
        Pipe the units together, and latter one will receive the former one's output result.

    :param units: Units to be piped together, should be no less than 1 unit.
    :return: A piped unit.

    Examples::
        - Simple pipe usage

        >>> from argsloader.units import add, mul, interval
        >>> u = add.by(2) >> mul.by(3)  # (x + 2) * 3
        >>> u(3)
        15
        >>> u(10)
        36

        - Use with a check unit

        >>> u = add.by(2) >> interval.lR(3, 11) # x + 2, then check (3, 11]
        >>> u(3)
        5
        >>> u(10)
        ValueParseError: Value not in interval - (3, 11] expected but 12 found.

    .. warning::
        The function :func:`_cpipe` is not recommended being used directly, \
        operator ``>>`` should be used instead.
    """

    return PipeUnit(*PipeUnit._chain_iter(*units))


class AndUnit(_IChainUnit):
    """
    Overview:
        Unit for chain all the units with ``and`` logic together.
    """

    def __init__(self, *units: BaseUnit):
        """
        Constructor of :class:`PipeUnit`.

        :param units: Unit to be chained with ``and`` logic together.
        """
        _IChainUnit.__init__(self, *units)

    def _easy_process(self, v: PValue, proxy: UnitProcessProxy) -> ParseResult:
        lastv, rs, valid = None, [], True
        for unit in self._units:
            curres = unit._process(v)
            rs.append(curres)
            if not curres.status.valid:
                valid = False
            else:
                lastv = curres.result

        if valid:
            return proxy.success(lastv, rs)
        else:
            return proxy.error(None, rs)


# noinspection PyProtectedMember
def _cand(*units) -> AndUnit:
    """
    Overview:
        Chain the units with ``and`` logic together, all the units will be checked together.

    :param units: Units to be chained together, should be no less than 1 unit.
    :return: A and-chained unit.

    Examples::
        >>> from argsloader.units import is_type, interval
        >>> u = is_type(int) & interval.lR(3, 10)
        >>> u(3)
        ValueParseError: Value not in interval - (3, 10] expected but 3 found.
        >>> u(10)
        10
        >>> u(3.0)
        TypeParseError: Value type not match - int expected but float found.

    .. note::
        If all the units in :class:`AndUnit` have succeeded, the last unit's result will be the final \
        result of this :class:`AndUnit`. For example,

        >>> from argsloader.units import is_type, interval, add
        >>> u = is_type(int) & (add.by(2) >> interval.lR(5, 12))
        >>> u(10)
        12

    .. note::
        All the units in :class:`AndUnit` will be executed, and all the errors will be displayed when \
        method :meth:`argsloader.units.base.BaseUnit.call` is called. For example,

        >>> from argsloader.units import is_type, interval
        >>> u = is_type(int) & interval.lR(3, 10)
        >>> u.call(3)
        argsloader.base.exception.MultipleParseError: (1 error)
          <root>: ValueParseError: Value not in interval - (3, 10] expected but 3 found.
        >>> u.call(10)
        10
        >>> u.call(3.0)
        argsloader.base.exception.MultipleParseError: (2 errors)
          <root>: TypeParseError: Value type not match - int expected but float found.
          <root>: ValueParseError: Value not in interval - (3, 10] expected but 3.0 found.

    .. warning::
        The function :func:`_cand` is not recommended being used directly, \
        operator ``&`` should be used instead.
    """
    return AndUnit(*AndUnit._chain_iter(*units))


class OrUnit(_IChainUnit):
    """
    Overview:
        Unit for chain all the units with ``or`` logic together.
    """

    def __init__(self, *units: BaseUnit):
        """
        Constructor of :class:`PipeUnit`.

        :param units: Unit to be chained with ``or`` logic together.
        """
        _IChainUnit.__init__(self, *units)

    def _easy_process(self, v: PValue, proxy: UnitProcessProxy) -> ParseResult:
        firstv, rs, invalid = None, [], True
        for unit in self._units:
            if invalid:
                curres = unit._process(v)
                rs.append(curres)
                if curres.status.valid:
                    invalid = False
                    firstv = curres.result
            else:
                rs.append(unit._skip(v))

        if not invalid:
            return proxy.success(firstv, rs)
        else:
            return proxy.error(None, rs)


# noinspection PyProtectedMember
def _cor(*units) -> OrUnit:
    """
    Overview:
        Chain the units with ``or`` logic together, all the units will be checked together.

    :param units: Units to be chained together, should be no less than 1 unit.
    :return: A or-chained unit.

    Examples::
        >>> from argsloader.units import is_type, interval
        >>> u = is_type(int) | interval.lR(3, 10)
        >>> u(3)
        3
        >>> u(10)
        10
        >>> u(3.0)
        TypeParseError: Value type not match - int expected but float found.

    .. note::
        The processing process will be terminated once one unit has succeeded, the latter units will be \
        skipped, and the success unit's return value will be used as the final result. For example,

        >>> from argsloader.units import is_type, interval, add, mul
        >>> u = (mul.by(3) >> is_type(int)) | (add.by(2) >> interval.lR(5, 12))
        >>> u(10)  # 10 * 3
        30
        >>> u(6.0)  # 6.0 + 2
        8.0

    .. note::
        If all the units in :class:`AndUnit` have failed, all the errors will be displayed when \
        method :meth:`argsloader.units.base.BaseUnit.call` is called. For example,

        >>> from argsloader.units import is_type, interval
        >>> u = is_type(int) | interval.lR(3, 10)
        >>> u.call(3)
        3
        >>> u.call(10)
        10
        >>> u.call(3.0)
        argsloader.base.exception.MultipleParseError: (2 errors)
          <root>: TypeParseError: Value type not match - int expected but float found.
          <root>: ValueParseError: Value not in interval - (3, 10] expected but 3.0 found.

    .. warning::
        The function :func:`_cor` is not recommended being used directly, \
        operator ``|`` should be used instead.
    """
    return OrUnit(*OrUnit._chain_iter(*units))
