from enum import IntEnum, unique
from typing import Optional, Union, Iterator, Tuple

from hbutils.collection import nested_walk
from hbutils.model import get_repr_info, int_enum_loads

from .exception import ParseError, MultipleParseError, SkippedParseError
from .value import PValue


class _BaseChildProxy:
    def __init__(self, children):
        self._children = children
        if not isinstance(self._children, (dict, list, tuple)):
            raise ValueError(f'Invalid type of children - {repr(type(children))}.')

    def __getitem__(self, item) -> Union['ParseResultChildProxy', object]:
        if self._children is not None:
            child = self._children[item]
            if isinstance(child, (dict, list, tuple)):
                return ParseResultChildProxy(child)
            else:
                return child
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
                    yield key, value
        elif isinstance(self._children, (tuple, list)):
            for i, value in enumerate(self._children):
                if isinstance(value, (dict, list, tuple)):
                    yield i, ParseResultChildProxy(value)
                else:
                    yield i, value
        else:
            return iter([])


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


class ParseResult(_BaseChildProxy):
    def __init__(self, input_: Optional[PValue], unit,
                 status: ResultStatus, result: Optional[PValue],
                 error: Optional[ParseError], children=None):
        _BaseChildProxy.__init__(self, children or {})

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

    def act(self):
        if self.__status.processed:
            if self.__status.valid:
                return self.result.value
            else:
                raise MultipleParseError(list(self._iter_errors()))
        else:
            raise SkippedParseError(self)
