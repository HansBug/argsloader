import os
import re
from textwrap import indent
from typing import Type, Tuple, List

from cachetools import cached
from hbutils.model import asitems, accessor, visual
from hbutils.reflection import class_wraps
from hbutils.string import plural_word

from .value import PValue


class BaseParseError(Exception):
    """
    Overview:
        Base class of all the parse errors.

    .. note::
        This class is only used as base class of :class:`argsloader.base.exception.ParseError`, \
        :class:`argsloader.base.exception.MultipleParseError` and :class:`argsloader.base.exception.SkippedParseError`.
    """
    pass


@accessor(readonly=True)
@visual(show_id=True)
@asitems(['message', 'unit', 'value', 'info'])
class ParseError(BaseParseError):
    """
    Overview:
        Error when parse one piece of data.
    """

    def __init__(self, message: str, unit, value: PValue, info: Tuple[object, ...]):
        """
        Constructor of class :class:`argsloader.base.exception.ParseError`.

        :param message: String message.
        :param unit: Unit which cause this error.
        :param value: Value passed in.
        :param info: Extra information.
        """
        BaseParseError.__init__(self, message, *info)
        self.__message = message
        self.__unit = unit
        self.__value = value
        self.__info = info


_EXCEPTION_NAME = re.compile('^([a-zA-Z0-9_]*)(Error|Exception)$')
_EXCEPTION_CLASSES = {}


@cached(_EXCEPTION_CLASSES)
def wrap_exception_class(cls: Type[Exception]) -> Type[ParseError]:
    """
    Wrap exception class to inherit :class:`argsloader.base.exception.ParseError`.

    :param cls: Class to be wrapped.
    :return: Wrapped exception class, which should be subclass of both \
        ``cls`` and :class:`argsloader.base.exception.ParseError`.

    Examples::
        >>> from argsloader.base import wrap_exception_class, ParseError
        >>> err = wrap_exception_class(ValueError)
        >>> err
        <class 'ValueParseError'>
        >>> issubclass(err, ParseError)
        True
        >>> issubclass(err, ValueError)
        True
    """
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
    """
    Wrap exception object to new exception object with wrapped class.

    :param ex: Original exception.
    :param unit: Unit which cause this exception.
    :param value: Value passed in.
    :return: Wrapped exception object, which should be an instance of \
        ``type(ex)`` and :class:`argsloader.base.exception.ParseError`.

    Examples::
        >>> from argsloader.base import wrap_exception, ParseError
        >>> err = wrap_exception(ValueError('this is message', 2, 3, 4), 'unit', 'value')
        >>> err
        <ValueParseError 0x7f13877146a8 message: 'this is message', unit: 'unit', value: 'value', info: (2, 3, 4)>
        >>> isinstance(err, ParseError)
        True
        >>> isinstance(err, ValueError)
        True
        >>> err.message
        'this is message'
        >>> err.unit
        'unit'
        >>> err.value
        'value'
        >>> err.info
        (2, 3, 4)
    """
    # noinspection PyCallingNonCallable
    return wrap_exception_class(type(ex))(ex, unit, value).with_traceback(ex.__traceback__)


class MultipleParseError(BaseParseError):
    """
    Overview:
        Full result of one parsing process.

        Can be seen as collection of :class:`argsloader.base.exception.ParseError`.
    """

    def __init__(self, items: List[Tuple[PValue, ParseError]]):
        """
        Constructor of class :class:`argsloader.base.exception.MultipleParseError`.

        :param items: Parse error items.
        """
        self.__items = list((pv, err) for pv, err in items)

    @property
    def items(self) -> List[Tuple[PValue, ParseError]]:
        """
        Parse error items.
        """
        return self.__items

    @classmethod
    def _display_item(cls, item):
        pvalue, error = item
        rep_str = '.'.join(('<root>', *map(str, pvalue.position)))
        error_str = error.message
        return f'{rep_str}: {type(error).__name__}: {error_str}'

    def __repr__(self):
        return f'<{type(self).__name__} ({plural_word(len(self.__items), "error")}){os.linesep}' \
               f'{indent(os.linesep.join(map(self._display_item, self.__items)), prefix="  ")}' \
               f'{os.linesep}>'

    def __str__(self):
        return f'({plural_word(len(self.__items), "error")}){os.linesep}' \
               f'{indent(os.linesep.join(map(self._display_item, self.__items)), prefix="  ")}'


@accessor(readonly=True)
@asitems(['unit'])
class SkippedParseError(BaseParseError):
    """
    Overview:
        Error used when parsing process is skipped due to the forwarded error.
    """

    def __init__(self, unit):
        """
        Constructor of class :class:`argsloader.base.exception.SkippedParseError`.

        :param unit: Unit which should do this parsing process.
        """
        BaseParseError.__init__(self, ('Parsing is skipped due the forward-side errors.', unit))
        self.__unit = unit
