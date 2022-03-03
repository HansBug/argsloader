from typing import Tuple

from .base import BaseUnit, _UnitProcessProxy, _to_unit
from ..base import ParseResult, PValue


class PipeUnit(BaseUnit):
    def __init__(self, unit: BaseUnit, *units: BaseUnit):
        self._units: Tuple[BaseUnit, ...] = tuple(map(_to_unit, (unit, *units)))

    def _easy_process(self, v: PValue, proxy: _UnitProcessProxy) -> ParseResult:
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

    @classmethod
    def pipe(cls, *units) -> 'PipeUnit':
        actual_units = []
        for unit in units:
            if isinstance(unit, PipeUnit):
                for iu in unit._units:
                    actual_units.append(iu)
            else:
                actual_units.append(unit)

        return cls(*actual_units)


def pipe(*units) -> PipeUnit:
    return PipeUnit.pipe(*units)


class AndUnit(BaseUnit):
    def __init__(self, unit: BaseUnit, *units: BaseUnit):
        self._units: Tuple[BaseUnit, ...] = tuple(map(_to_unit, (unit, *units)))

    def _easy_process(self, v: PValue, proxy: _UnitProcessProxy) -> ParseResult:
        lastv, rs, valid = None, [], True
        for unit in self._units:
            if valid:
                curres = unit._process(v)
                rs.append(curres)
                if not curres.status.valid:
                    valid = False
                else:
                    lastv = curres.result
            else:
                rs.append(unit._skip(v))

        if valid:
            return proxy.success(lastv, rs)
        else:
            return proxy.error(None, rs)

    @classmethod
    def and_(cls, *units) -> 'AndUnit':
        actual_units = []
        for unit in units:
            if isinstance(unit, AndUnit):
                for iu in unit._units:
                    actual_units.append(iu)
            else:
                actual_units.append(unit)

        return cls(*actual_units)


def and_(*units) -> AndUnit:
    return AndUnit.and_(*units)


class OrUnit(BaseUnit):
    def __init__(self, unit: BaseUnit, *units: BaseUnit):
        self._units: Tuple[BaseUnit, ...] = tuple(map(_to_unit, (unit, *units)))

    def _easy_process(self, v: PValue, proxy: _UnitProcessProxy) -> ParseResult:
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

    @classmethod
    def or_(cls, *units) -> 'OrUnit':
        actual_units = []
        for unit in units:
            if isinstance(unit, OrUnit):
                for iu in unit._units:
                    actual_units.append(iu)
            else:
                actual_units.append(unit)

        return cls(*actual_units)


def or_(*units) -> OrUnit:
    return OrUnit.or_(*units)
