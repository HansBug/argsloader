from functools import lru_cache
from typing import Mapping, Any

from ..base import ParseResult, wrap_exception, ParseError, ResultStatus, PValue


class _UnitModel:
    def __call__(self, v):
        raise NotImplementedError  # pragma: no cover

    def call(self, v, err_mode='first'):
        raise NotImplementedError  # pragma: no cover

    def log(self, v) -> ParseResult:
        raise NotImplementedError  # pragma: no cover

    @property
    def validity(self) -> 'BaseUnit':
        raise NotImplementedError  # pragma: no cover


class _UncompletedUnit(_UnitModel):
    def _fail(self):
        raise NotImplementedError  # pragma: no cover

    def __call__(self, v):
        return self._fail()

    def call(self, v, err_mode='first'):
        return self._fail()

    def log(self, v) -> ParseResult:
        return self._fail()

    @property
    def validity(self) -> 'BaseUnit':
        return self._fail()


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
        if err is not None and not isinstance(err, ParseError):
            err = wrap_exception(err, self.__unit, self.__v)
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
    from .operator import pipe, and_, or_
    return pipe, and_, or_


class BaseUnit(_UnitModel):
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

    def log(self, v) -> ParseResult:
        return self._process(PValue(v, ()))

    @property
    def validity(self) -> 'BaseUnit':
        from .utils import validity
        return validity(self)

    def __rshift__(self, other) -> 'BaseUnit':
        pipe, _, _ = _get_ops()
        return pipe(self, _to_unit(other))

    def __rrshift__(self, other) -> 'BaseUnit':
        return _to_unit(other) >> self

    def __and__(self, other) -> 'BaseUnit':
        _, and_, _ = _get_ops()
        return and_(self, _to_unit(other))

    def __rand__(self, other) -> 'BaseUnit':
        return _to_unit(other) & self

    def __or__(self, other) -> 'BaseUnit':
        _, _, or_ = _get_ops()
        return or_(self, _to_unit(other))

    def __ror__(self, other) -> 'BaseUnit':
        return _to_unit(other) | self


class ValueUnit(BaseUnit):
    def __init__(self, value):
        self._value = value

    def _easy_process(self, v: PValue, proxy: _UnitProcessProxy) -> ParseResult:
        return proxy.success(v.val(self._value))


def raw(v):
    return ValueUnit(v)


def _to_unit(v) -> BaseUnit:
    if isinstance(v, _UncompletedUnit):
        getattr(v, '_fail')()
    if isinstance(v, BaseUnit):
        return v
    else:
        return raw(v)


class _TransformUnit(BaseUnit):
    __errors__ = ()
    __names__ = ()

    def __init__(self, *values):
        self._values = tuple(map(lambda x: x[1], zip(self.__names__, values)))

    def _transform(self, v: PValue, pres: Mapping[str, Any]) -> PValue:
        raise NotImplementedError  # pragma: no cover

    def _easy_process(self, v: PValue, proxy: _UnitProcessProxy) -> ParseResult:
        ovalues, valid = dict(zip(self.__names__, self._values)), True

        def _recursion(ov):
            nonlocal valid

            if isinstance(ov, dict):
                vs, rs = {}, {}
                for name_, iv in ov.items():
                    v_, res = _recursion(iv)
                    vs[name_] = v_
                    rs[name_] = res
                tp = type(ov)
                return tp(vs), tp(rs)
            elif isinstance(ov, (list, tuple)):
                vs, rs = [], []
                for iv in ov:
                    v_, res = _recursion(iv)
                    vs.append(v_)
                    rs.append(res)
                tp = type(ov)
                return tp(vs), tp(rs)
            else:
                _curu = _to_unit(ov)
                if valid:
                    res = _curu._process(v)
                    if res.status.valid:
                        return res.result.value, res
                    else:
                        valid = False
                        return None, res
                else:
                    return None, _curu._skip(v)

        pvalues, rvalues = _recursion(ovalues)
        if valid:
            pres, error = None, None
            try:
                pres = self._transform(v, pvalues)
            except ParseError as err:
                error = err
            except self.__errors__ as err:
                error = err

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
        raise NotImplementedError  # pragma: no cover
