from typing import Mapping, Any

from hbutils.collection import nested_map
from hbutils.string import plural_word

from .base import BaseUnit, _to_unit, UnitProcessProxy
from ..base import PValue, ParseResult, ParseError


class TransformUnit(BaseUnit):
    """
    Overview:
        Common transform unit.
    """
    __errors__ = ()
    __names__ = ()

    def __init__(self, *values):
        """
        Constructor of class :class:`argsloader.units.base.TransformUnit`.

        :param values: Values need to be pre-processed, should be mapped one-to-one with ``__names__``.
        """
        if len(self.__names__) != len(values):
            raise TypeError(f'{type(self).__name__} should accept {plural_word(len(self.__names__), "word")}, '
                            f'but {plural_word(len(values), "word")} found.')

        self._values = nested_map(_to_unit, tuple(values))

    def _transform(self, v: PValue, pres: Mapping[str, Any]) -> PValue:
        """
        Transform method.

        :param v: Original ``PValue`` object.
        :param pres: Pre-processed values.
        :return: Returned ``PValue`` object.
        :raises Exception: Raised exception which is instance of ``__errors__`` will be processed.
        """
        raise NotImplementedError  # pragma: no cover

    def _easy_process(self, v: PValue, proxy: UnitProcessProxy) -> ParseResult:
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
                        return res.result, res
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

    def _rinfo(self):
        return [], [(name, val) for name, val in zip(self.__names__, self._values)]


class CalculateUnit(TransformUnit):
    """
    Overview:
        Simple value calculation unit.
    """

    def _transform(self, v: PValue, pres: Mapping[str, Any]) -> PValue:
        return v.val(self._calculate(
            v.value, nested_map(lambda x: x.value, pres)
        ))

    def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
        """
        Calculation method.

        :param v: Original value.
        :param pres: Pre-processed values.
        :return: Returned value.
        :raises Exception: Raised exception which is instance of ``__errors__`` will be processed.
        """
        raise NotImplementedError  # pragma: no cover
