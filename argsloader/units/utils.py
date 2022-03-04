from typing import Mapping, Any

from .base import _CalculateUnit, BaseUnit, _UnitProcessProxy, _to_unit, _TransformUnit
from ..base import PValue, ParseResult, wrap_exception


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
        self._unit = _to_unit(unit)

    def _easy_process(self, v: PValue, proxy: _UnitProcessProxy) -> ParseResult:
        result: ParseResult = self._unit._process(v)
        return proxy.success(v.val(result.status.valid), {'unit': result})


def validity(unit) -> ValidUnit:
    return ValidUnit(unit)


class ErrorUnit(_TransformUnit):
    __names__ = ('condition', 'errcls', 'args')

    def __init__(self, condition, errcls, *args):
        _TransformUnit.__init__(self, condition, errcls, args)

    def _transform(self, v: PValue, pres: Mapping[str, Any]) -> PValue:
        if not pres['condition']:
            return v
        else:
            errcls = pres['errcls']
            args = tuple(pres['args'])
            raise wrap_exception(errcls(*args), self, v)


def error(condition, errcls, *args) -> ErrorUnit:
    return ErrorUnit(condition, errcls, *args)


def validate(val, condition, errcls, *args):
    from .mathop import not_
    return check(_to_unit(val) >> error(not_(_to_unit(condition)), errcls, *args))
