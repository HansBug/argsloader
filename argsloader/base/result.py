from enum import IntEnum, unique
from typing import Optional, Union, Iterator, Tuple

from hbutils.collection import nested_walk
from hbutils.model import get_repr_info, int_enum_loads, raw_support, asitems, hasheq

from .exception import ParseError, MultipleParseError, SkippedParseError
from .value import PValue

raw_res, unraw_res, _RawResProxy = raw_support(
    lambda x: isinstance(x, (dict, list, tuple)),
    'raw_res', 'unraw_res', '_RawResProxy',
)
_NoneType = type(None)


class _BaseChildProxy:
    def __init__(self, children):
        self._children = children
        if not isinstance(self._children, (dict, list, tuple, _NoneType)):
            raise ValueError(f'Invalid type of children - {repr(type(children))}.')

    def __getitem__(self, item) -> Union['ParseResultChildProxy', object]:
        if self._children is not None:
            child = self._children[item]
            if isinstance(child, (dict, list, tuple)):
                return ParseResultChildProxy(child)
            else:
                return unraw_res(child)
        else:
            raise KeyError(f'Key {repr(item)} not found.')

    def __contains__(self, item) -> bool:
        if isinstance(self._children, dict):
            return item in self._children
        elif isinstance(self._children, (list, tuple)):
            return item in range(len(self._children))
        else:
            return False

    def keys(self):
        if isinstance(self._children, dict):
            return self._children.keys()
        elif isinstance(self._children, (tuple, list)):
            return range(len(self._children))
        else:
            return []

    def items(self):
        if isinstance(self._children, dict):
            for key, value in self._children.items():
                if isinstance(value, (dict, list, tuple)):
                    yield key, ParseResultChildProxy(value)
                else:
                    yield key, unraw_res(value)
        elif isinstance(self._children, (tuple, list)):
            for i, value in enumerate(self._children):
                if isinstance(value, (dict, list, tuple)):
                    yield i, ParseResultChildProxy(value)
                else:
                    yield i, unraw_res(value)
        else:
            return iter([])


@hasheq()
@asitems(['_children'])
class ParseResultChildProxy(_BaseChildProxy):
    pass


@int_enum_loads(name_preprocess=str.upper)
@unique
class ResultStatus(IntEnum):
    SKIPPED = 0
    SUCCESS = 1
    ERROR = 2

    @property
    def valid(self):
        return self == self.SUCCESS

    @property
    def processed(self):
        return self != self.SKIPPED


@int_enum_loads(name_preprocess=str.upper)
@unique
class ErrMode(IntEnum):
    FIRST = 1
    TRY_ALL = 2
    ALL = 3


class ParseResult(_BaseChildProxy):
    def __init__(self, input_: Optional[PValue], unit,
                 status, result: Optional[PValue],
                 error: Optional[ParseError], children=None):
        _BaseChildProxy.__init__(self, children)

        self.__input = input_
        self.__unit = unit

        self.__status: ResultStatus = ResultStatus.loads(status)
        self.__result = result if self.__status.valid else None
        self.__error = error if self.__status.processed else None

    def __repr__(self):
        return get_repr_info(self.__class__, [
            ('input', lambda: self.input, lambda: self.__status.processed),
            ('status', lambda: self.__status.name),
            ('result', lambda: self.result, lambda: self.__status.valid),
            (
                'error',
                lambda: self.error.message if self.__error is not None else '<caused by prerequisites>',
                lambda: self.__status.processed and not self.__status.valid,
            ),
        ])

    @property
    def input(self) -> Optional[PValue]:
        return self.__input

    @property
    def unit(self):
        return self.__unit

    @property
    def status(self) -> ResultStatus:
        return self.__status

    @property
    def result(self) -> Optional[PValue]:
        return self.__result

    @property
    def error(self) -> Optional[ParseError]:
        return self.__error

    def _iter_errors(self) -> Iterator[Tuple[PValue, ParseError]]:
        if self.__status.processed and not self.__status.valid:
            if self.error is not None:
                yield self.input, self.error

            for _, v in nested_walk(self._children):
                if isinstance(v, ParseResult):
                    yield from v._iter_errors()

    def _first_error(self):
        try:
            pval, error = next(self._iter_errors())
            return error
        except StopIteration:  # pragma: no cover
            return None  # pragma: no cover

    def _try_full_error(self):
        all_errors = list(self._iter_errors())
        if len(all_errors) > 1:
            return MultipleParseError(all_errors)
        elif len(all_errors) == 1:
            pval, error = all_errors[0]
            return error
        else:
            return None  # pragma: no cover

    def _full_error(self):
        all_errors = list(self._iter_errors())
        if all_errors:
            return MultipleParseError(all_errors)
        else:
            return None  # pragma: no cover

    def act(self, err_mode):
        err_mode = ErrMode.loads(err_mode)
        if self.__status.processed:
            if self.__status.valid:
                return self.result.value
            else:
                if err_mode == ErrMode.FIRST:
                    raise self._first_error()
                elif err_mode == ErrMode.TRY_ALL:
                    raise self._try_full_error()
                elif err_mode == ErrMode.ALL:
                    raise self._full_error()
        else:
            raise SkippedParseError(self)
