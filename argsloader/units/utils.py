from typing import Mapping, Any, List, Tuple

from hbutils.design import SingletonMark

from .base import _CalculateUnit, BaseUnit, _UnitProcessProxy, _to_unit, _TransformUnit, _UncompletedUnit
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


def fail(errcls, *args) -> ErrorUnit:
    return error(True, errcls, *args)


_ELSE_STATEMENT = SingletonMark('ELSE_STATEMENT')


class _IfProxy(_UncompletedUnit):
    def __init__(self, statements):
        self._statements = statements

    def elif_(self, cond, val) -> '_IfProxy':
        return _IfProxy([*self._statements, (_to_unit(cond), _to_unit(val))])

    def else_(self, val) -> 'IfUnit':
        return IfUnit([*self._statements, (_ELSE_STATEMENT, _to_unit(val))])

    def _fail(self):
        raise SyntaxError('Uncompleted if statement unit - else statement expected but not found.')


class IfUnit(BaseUnit):
    def __init__(self, statements: List[Tuple[BaseUnit, BaseUnit]]):
        self._statements = statements

    def _easy_process(self, v: PValue, proxy: _UnitProcessProxy) -> ParseResult:
        completed, valid, result, record = False, True, None, []
        for cond, val in self._statements:
            cond = cond if cond is not _ELSE_STATEMENT else _to_unit(True)
            if not completed:
                cres = cond._process(v)
                if cres.status.valid:
                    if cres.result.value:
                        vres = val._process(v)
                        record.append((cres, vres))
                        if vres.status.valid:
                            completed = True
                            valid = True
                            result = vres.result
                        else:
                            completed = True
                            valid = False
                    else:
                        record.append((cres, val._skip(v)))
                else:
                    completed = True
                    valid = False
                    record.append((cres, val._skip(v)))
            else:
                record.append((cond._skip(v), val._skip(v)))

        if valid:
            return proxy.success(result, record)
        else:
            return proxy.error(None, record)


def if_(conf, val) -> _IfProxy:
    return _IfProxy([(_to_unit(conf), _to_unit(val))])
