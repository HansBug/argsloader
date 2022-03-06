from typing import Tuple, Iterator

from .base import BaseUnit, UnitProcessProxy, _to_unit
from ..base import ParseResult, PValue


class _ChainUnit(BaseUnit):
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


class PipeUnit(_ChainUnit):
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
def pipe(*units) -> PipeUnit:
    return PipeUnit(*PipeUnit._chain_iter(*units))


class AndUnit(_ChainUnit):
    def _easy_process(self, v: PValue, proxy: UnitProcessProxy) -> ParseResult:
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


# noinspection PyProtectedMember
def and_(*units) -> AndUnit:
    return AndUnit(*AndUnit._chain_iter(*units))


class OrUnit(_ChainUnit):
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
def or_(*units) -> OrUnit:
    return OrUnit(*OrUnit._chain_iter(*units))
