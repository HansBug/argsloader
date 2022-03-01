import os
import re
from textwrap import indent
from typing import Type

from cachetools import cached
from hbutils.model import asitems, accessor, visual
from hbutils.reflection import class_wraps
from hbutils.string import plural_word


class BaseParseError(Exception):
    pass


@accessor(readonly=True)
@visual(show_id=True)
@asitems(['message', 'unit', 'value', 'info'])
class ParseError(BaseParseError):
    def __init__(self, message, unit, value, info=None):
        Exception.__init__(self, (message, unit, value, info))
        self.__message = message
        self.__unit = unit
        self.__value = value
        self.__info = info


_EXCEPTION_NAME = re.compile('^([a-zA-Z0-9_]*)(Error|Exception)$')
_EXCEPTION_CLASSES = {}


@cached(_EXCEPTION_CLASSES)
def wrap_exception_class(cls: Type[Exception]) -> Type[ParseError]:
    matching = _EXCEPTION_NAME.fullmatch(cls.__name__)
    if matching:
        @class_wraps(cls)
        class _ParseError(cls, ParseError):
            def __init__(self, exc: Exception, unit, value):
                args = tuple(exc.args) if isinstance(exc.args, (list, tuple)) else (exc.args,)
                ParseError.__init__(self, args[0], unit, value, args[1:])

        _ParseError.__name__ = f'{matching[1]}Parse{matching[2]}'
        return _ParseError

    else:
        raise NameError(f'Unrecognizable exception name - {repr(cls.__name__)}.')


def wrap_exception(ex: Exception, unit, value) -> ParseError:
    cls = ex.__class__
    # noinspection PyCallingNonCallable
    return wrap_exception_class(cls)(ex, unit, value)


class MultipleParseError(BaseParseError):
    def __init__(self, items):
        BaseParseError.__init__(self, items)
        self.__items = items

    @property
    def items(self):
        return self.__items

    @classmethod
    def _display_item(cls, item):
        position, error = item
        rep_str = '.'.join(('<root>', *position.represent()))
        error_str = error.message
        return f'{rep_str}: {error_str}'

    def __repr__(self):
        return f'<{type(self).__name__} ({plural_word(len(self.__items), "error")}){os.linesep}' \
               f'{indent(os.linesep.join(map(self._display_item, self.__items)), prefix="  ")}' \
               f'{os.linesep}>'

    def __str__(self):
        return f'({plural_word(len(self.__items), "error")}){os.linesep}' \
               f'{indent(os.linesep.join(map(self._display_item, self.__items)), prefix="  ")}'
