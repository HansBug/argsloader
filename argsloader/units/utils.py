from typing import Mapping, Any

from .base import _CalculateUnit, BaseUnit, _UnitProcessProxy
from ..base import PValue, ParseResult


class KeepUnit(_CalculateUnit):
    def __init__(self):
        _CalculateUnit.__init__(self)

    def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
        return v


_keep_unit = KeepUnit()


def keep() -> KeepUnit:
    return _keep_unit


class CheckUnit(_CalculateUnit):
    __names__ = ('unit',)

    def __init__(self, unit):
        _CalculateUnit.__init__(self, unit)

    def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
        return v


def check(unit) -> CheckUnit:
    return CheckUnit(unit)


class ValidUnit(BaseUnit):
    def __init__(self, unit: BaseUnit):
        self._unit = unit

    def _easy_process(self, v: PValue, proxy: _UnitProcessProxy) -> ParseResult:
        result: ParseResult = self._unit._process(v)
        return proxy.success(v.val(result.status.valid), {'unit': result})


def valid(unit) -> ValidUnit:
    return ValidUnit(unit)
