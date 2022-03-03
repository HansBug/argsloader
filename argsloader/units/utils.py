from typing import Mapping, Any

from .base import _CalculateUnit


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
