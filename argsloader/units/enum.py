import re
from enum import Enum, Flag
from functools import reduce
from operator import __or__
from typing import Type

import inflection

from .base import BaseUnit, UnitProcessProxy
from ..base import PValue, ParseResult


def _name_align(name: str):
    return inflection.underscore(name.strip()).lower()


ENUM_SPLITTER = re.compile('[,;:| \\t]+')


class EnumUnit(BaseUnit):
    """
    Overview:
        Unit for parsing enum object.
    """

    def __init__(self, enum_cls: Type[Enum]):
        """
        Constructor of :class:`EnumUnit`.

        :param enum_cls: Enum class, should be a subclass of ``Enum``.
        """
        self._enum_cls = enum_cls
        self._name_to_enums = {
            _name_align(name): value
            for name, value in self._enum_cls.__members__.items()
        }
        self._is_flag = issubclass(enum_cls, Flag)

    def _single_process(self, v):
        if isinstance(v, self._enum_cls):
            return v
        else:
            try:
                return self._enum_cls(v)
            except (TypeError, ValueError):
                if isinstance(v, str):
                    _name = _name_align(v)
                    if _name in self._name_to_enums:
                        return self._name_to_enums[_name]

                raise ValueError(f'Value is expected to be a {self._enum_cls.__name__} object, '
                                 f'but {repr(v)} found actually.')

    def _full_process(self, v):
        if self._is_flag and isinstance(v, (str, list, tuple, set)):
            items = []
            if isinstance(v, str):
                for item in filter(bool, ENUM_SPLITTER.split(v)):
                    try:
                        ii = int(item)
                        items.append(self._single_process(ii))
                    except (TypeError, ValueError):
                        items.append(self._single_process(item))
            else:
                for item in v:
                    items.append(self._single_process(item))

            if items:
                return reduce(__or__, items)
            else:
                return self._enum_cls(0)
        else:
            return self._single_process(v)

    def _easy_process(self, v: PValue, proxy: UnitProcessProxy) -> ParseResult:
        try:
            return proxy.success(v.val(self._full_process(v.value)))
        except ValueError as err:
            return proxy.error(err)

    def _rinfo(self):
        return [('enum', self._enum_cls)], []


def enum(ecls: Type[Enum]) -> EnumUnit:
    """
    Overview:
        Get a unit for parsing enum.

    :param ecls: Enum class, should be a subclass of ``Enum``.
    :return: A unit for parsing enum.

    Examples::
        - Basic enum parsing

        >>> from enum import Enum
        >>> from argsloader.units import enum
        >>> class Color(Enum):
        ...     RED = 1
        ...     GREEN = 2
        ...     BLUE = 4
        ...
        >>> u = enum(Color)
        >>> u(2)
        <Color.GREEN: 2>
        >>> u('red')
        <Color.RED: 1>
        >>> u('BLUE')
        <Color.BLUE: 4>
        >>> u(Color.GREEN)
        <Color.GREEN: 2>
        >>> u(3)
        ValueParseError: Value is expected to be a Color object, but 3 found actually.

        - Flag enum parsing

        >>> from enum import Flag
        >>> from argsloader.units import enum
        >>> class Color(Flag):
        ...     RED = 1
        ...     GREEN = 2
        ...     BLUE = 4
        ...     WHITE = RED | GREEN | BLUE
        ...
        >>> u = enum(Color)
        >>> u(2)
        <Color.GREEN: 2>
        >>> u('red')
        <Color.RED: 1>
        >>> u('White')
        <Color.WHITE: 7>
        >>> u(6)
        <Color.BLUE|GREEN: 6>
        >>> u('red, blue')
        <Color.BLUE|RED: 5>
        >>> u('green, 4')
        <Color.BLUE|GREEN: 6>
        >>> u('')
        <Color.0: 0>
        >>> u([1, Color.BLUE])
        <Color.BLUE|RED: 5>

    .. note::
        Function :func:`enum` is used based on ``Enum`` class, which you need to \
        build an enum class before this. For further information, see the following pages:

        - `enum - Creating an Enum <https://docs.python.org/3/library/enum.html#creating-an-enum>`_
        - `enum - Flag <https://docs.python.org/3/library/enum.html#flag>`_
    """
    if isinstance(ecls, type) and issubclass(ecls, Enum):
        return EnumUnit(ecls)
    else:
        raise TypeError(f'A subclass of {repr(Enum)} expected, but {repr(ecls)} found.')
