from functools import lru_cache
from typing import Mapping, Any

from hbutils.string import plural_word

from ..base import ParseResult, wrap_exception, ParseError, ResultStatus, PValue


class _UnitProcessProxy:
    def __init__(self, unit: 'BaseUnit', v: PValue):
        self.__unit = unit
        self.__v = v

    def success(self, res: PValue, children=None) -> ParseResult:
        return ParseResult(
            self.__v, self.__unit,
            ResultStatus.SUCCESS, res, None, children
        )

    def error(self, err, children=None) -> ParseResult:
        return ParseResult(
            self.__v, self.__unit,
            ResultStatus.ERROR, None, err, children
        )

    def skipped(self) -> ParseResult:
        return ParseResult(
            None, self.__unit,
            ResultStatus.SKIPPED, None, None, None
        )


@lru_cache()
def _get_ops():
    from .operator import pipe, and_
    return pipe, and_, None


class BaseUnit:
    def _process(self, v: PValue) -> ParseResult:
        return self._easy_process(v, _UnitProcessProxy(self, v))

    def _easy_process(self, v: PValue, proxy: _UnitProcessProxy) -> ParseResult:
        raise NotImplementedError  # pragma: no cover

    def _skip(self, v: PValue) -> ParseResult:
        return _UnitProcessProxy(self, v).skipped()

    def __call__(self, v):
        return self.call(v)

    def call(self, v, err_mode='first'):
        return self._process(PValue(v, ())).act(err_mode)

    def log(self, v):
        return self._process(PValue(v, ()))

    def __rshift__(self, other: 'BaseUnit'):
        if isinstance(other, BaseUnit):
            pipe, _, _ = _get_ops()
            return pipe(self, other)
        else:
            return self.__rshift__(_to_unit(other))

    def __rrshift__(self, other):
        return _to_unit(other) >> self

    def __and__(self, other):
        if isinstance(other, BaseUnit):
            _, and_, _ = _get_ops()
            return and_(self, other)
        else:
            return self.__and__(_to_unit(other))

    def __rand__(self, other):
        return _to_unit(other) & self


class ValueUnit(BaseUnit):
    def __init__(self, value):
        self._value = value

    def _easy_process(self, v: PValue, proxy: _UnitProcessProxy) -> ParseResult:
        return proxy.success(v.val(self._value))


def raw(v):
    return ValueUnit(v)


def _to_unit(v):
    if isinstance(v, BaseUnit):
        return v
    else:
        return raw(v)


class _TransformUnit(BaseUnit):
    __errors__ = ()
    __names__ = ()

    def __init__(self, *values):
        if len(values) != len(self.__names__):
            raise ValueError(f'{plural_word(len(self.__names__), "value")} expected '
                             f'in {type(self).__name__}.__init__, '
                             f'but {plural_word(len(values), "value")} found actually!')
        self._values = tuple(map(_to_unit, values))

    def _transform(self, v: PValue, pres: Mapping[str, Any]) -> PValue:
        raise NotImplementedError

    def _easy_process(self, v: PValue, proxy: _UnitProcessProxy) -> ParseResult:
        rvalues, pvalues, valid = {}, {}, True
        for name, value in zip(self.__names__, self._values):
            if valid:
                curres = value._process(v)
                rvalues[name] = curres
                if curres.status.valid:
                    pvalues[name] = curres.result.value
                else:
                    valid = False
            else:
                curres = value._skip(v)
                rvalues[name] = curres

        if valid:
            pres, error = None, None
            try:
                pres = self._transform(v, pvalues)
            except ParseError as err:
                error = err
            except self.__errors__ as err:
                error = wrap_exception(err, self, v)

            if error is None:
                return proxy.success(pres, rvalues)
            else:
                return proxy.error(error, rvalues)
        else:
            return proxy.error(None, rvalues)


class _CalculateUnit(_TransformUnit):
    def _transform(self, v: PValue, pres: Mapping[str, Any]) -> PValue:
        return v.val(self._calculate(v.value, pres))

    def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
        raise NotImplementedError
