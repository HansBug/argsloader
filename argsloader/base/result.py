from typing import Optional, Union

from hbutils.collection import nested_walk
from hbutils.model import get_repr_info, raw_support

from .exception import ParseError, MultipleParseError
from .position import PathPosition

raw_result, unraw_result, _ = raw_support(
    lambda x: isinstance(x, (dict, list, tuple)),
    'raw_result', 'unraw_result', '_ResultRawProxy'
)


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
                return unraw_result(child)
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
                    yield key, unraw_result(value)
        elif isinstance(self._children, (tuple, list)):
            for i, value in enumerate(self._children):
                if isinstance(value, (dict, list, tuple)):
                    yield i, ParseResultChildProxy(value)
                else:
                    yield i, unraw_result(value)
        else:
            return iter([])


class ParseResultChildProxy(_BaseChildProxy):
    pass


class ParseResult(_BaseChildProxy):
    def __init__(self, input_, position: PathPosition, unit,
                 valid: bool, result, error: Optional[ParseError], children=None):
        _BaseChildProxy.__init__(self, children or {})

        self.__input = input_
        self.__position = position

        self.__unit = unit
        self.__valid = not not valid
        self.__result = result if self.__valid else None
        self.__error = error

    def __repr__(self):
        return get_repr_info(self.__class__, [
            ('position', lambda: self.position),
            ('input', lambda: self.input),
            ('result', lambda: self.result, lambda: self.__valid),
            (
                'error',
                lambda: self.error.message if self.__error is not None else '<caused by prerequisites>',
                lambda: not self.__valid
            ),
        ])

    @property
    def input(self):
        return self.__input

    @property
    def position(self) -> PathPosition:
        return self.__position

    @property
    def unit(self):
        return self.__unit

    @property
    def valid(self) -> bool:
        return self.__valid

    @property
    def result(self):
        return self.__result

    @property
    def error(self) -> Optional[ParseError]:
        return self.__error

    def _iter_errors(self):
        if not self.valid:
            if self.error is not None:
                yield self.position, self.error

            for _, v in nested_walk(self._children):
                if isinstance(v, ParseResult):
                    yield from v._iter_errors()

    def act(self):
        if self.valid:
            return self.result
        else:
            raise MultipleParseError(list(self._iter_errors()))
