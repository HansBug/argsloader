from typing import Tuple

from .base import BaseUnit
from ..base import PathPosition, ParseResult


class PipeUnit(BaseUnit):
    def __init__(self, unit: BaseUnit, *units: BaseUnit):
        self._units = (unit, *units)

    def _process(self, v, pos: PathPosition) -> Tuple[ParseResult, PathPosition]:
        curv, rs, valid = v, [], True
        for i, unit in enumerate(self._units):
            result, _ = unit._process(curv, pos)
            rs.append(result)
            if result.valid:
                curv = result.result
            else:
                valid = False
                break
        if valid:
            return ParseResult(v, pos, self, True, curv, None, rs), pos
        else:
            return ParseResult(v, pos, self, False, None, None, rs), pos

    @classmethod
    def pipe(cls, *units):
        actual_units = []
        for unit in units:
            if isinstance(unit, PipeUnit):
                for iu in unit._units:
                    actual_units.append(iu)
            else:
                actual_units.append(unit)

        return PipeUnit(*actual_units)


def pipe(*units) -> PipeUnit:
    return PipeUnit.pipe(*units)
