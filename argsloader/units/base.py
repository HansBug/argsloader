from typing import Tuple

from hbutils.string import plural_word

from ..base import PathPosition, ParseResult, wrap_exception, raw_result, ParseError


class BaseUnit:
    def _process(self, v, pos: PathPosition) -> Tuple[ParseResult, PathPosition]:
        raise NotImplementedError  # pragma: no cover

    def __call__(self, v):
        result, _ = self._process(v, PathPosition())
        return result.act()

    def log(self, v):
        result, _ = self._process(v, PathPosition())
        return result

    def __rshift__(self, other: 'BaseUnit'):
        if isinstance(other, BaseUnit):
            from .operator import pipe
            return pipe(self, other)
        else:
            raise TypeError(f'Type {repr(type(other))} is not supported for pipe operation.')


class _ValueBasedUnit(BaseUnit):
    __errors__ = ()
    __names__ = ()

    def __init__(self, *values):
        if len(values) != len(self.__names__):
            raise ValueError(f'{plural_word(len(self.__names__), "value")} expected '
                             f'in {type(self).__name__}.__init__, '
                             f'but {plural_word(len(values), "value")} found actually!')
        self._values = values

    def _validate(self, v, pres) -> object:
        raise NotImplementedError

    def _process(self, v, pos: PathPosition) -> Tuple[ParseResult, PathPosition]:
        rvalues, pvalues, valid = {}, {}, True
        for name, value in zip(self.__names__, self._values):
            if isinstance(value, BaseUnit):
                if valid:
                    ritem, _ = value._process(value, pos)
                    if ritem.valid:
                        rvalues[name] = ritem
                        pvalues[name] = ritem.result
                    else:
                        valid = False
                        break
                else:
                    continue
            else:
                rvalues[name] = raw_result(value)
                pvalues[name] = value

        if valid:
            result, error = None, None
            try:
                result = self._validate(v, pvalues)
            except ParseError as err:
                error = err
            except self.__errors__ as err:
                error = wrap_exception(err, self, v)

            return ParseResult(v, pos, self, error is None, result, error, rvalues), pos
        else:
            return ParseResult(v, pos, self, False, None, None, rvalues), pos
