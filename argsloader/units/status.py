from typing import Mapping, Any

from hbutils.collection import nested_map

from .build import TransformUnit
from ..base import PValue


class ChildPositionUnit(TransformUnit):
    """
    Overview:
        Unit for switching position to child level.
    """
    __names__ = ('children',)

    def __init__(self, *children):
        """
        Constructor of :class:`ChildPositionUnit`.

        :param children: Child levels, multiple levels are supported.
        """
        TransformUnit.__init__(self, children)

    def _transform(self, v: PValue, pres: Mapping[str, Any]) -> PValue:
        return v.child(*nested_map(lambda x: x.value, pres['children']))


def child(*children) -> ChildPositionUnit:
    """
    Overview:
        Switching position to child level, multiple levels are supported.

    :param children: Child levels.
    :return: A child position unit.

    Examples::
        >>> from argsloader.units import child, is_type
        >>> u = is_type(int)
        >>> u.call(1.0)
        argsloader.base.exception.MultipleParseError: (1 error)
          <root>: TypeParseError: Value type not match - int expected but float found.
        >>>
        >>> u = child('level') >> is_type(int)
        >>> u.call(1.0)
        argsloader.base.exception.MultipleParseError: (1 error)
          <root>.level: TypeParseError: Value type not match - int expected but float found.
        >>>
        >>> u = child('level', 2) >> is_type(int)
        >>> u.call(1.0)
        argsloader.base.exception.MultipleParseError: (1 error)
          <root>.level.2: TypeParseError: Value type not match - int expected but float found.
    """
    return ChildPositionUnit(*children)


class ParentPositionUnit(TransformUnit):
    """
    Overview:
        Unit for switching position to parent level.
    """
    __names__ = ('level',)

    def __init__(self, level):
        """
        Constructor of :class:`ParentPositionUnit`.

        :param level: Number of levels.
        """
        TransformUnit.__init__(self, level)

    def _transform(self, v: PValue, pres: Mapping[str, Any]) -> PValue:
        return v.parent(pres['level'].value)


def parent(level=1) -> ParentPositionUnit:
    """
    Overview:
        Switching position to parent level, multiple levels are supported.

    :param level: Number of levels, default is ``1``.
    :return: A parent position unit.

    Examples::
        >>> from argsloader.units import child, is_type, parent
        >>> u = child('level', 2) >> is_type(int)
        >>> u.call(1.0)  # no parent level, just <root>.level.2
        argsloader.base.exception.MultipleParseError: (1 error)
          <root>.level.2: TypeParseError: Value type not match - int expected but float found.
        >>>
        >>> u = child('level', 2) >> parent() >> is_type(int)
        >>> u.call(1.0)  # parent 1 level, <root>.level
        argsloader.base.exception.MultipleParseError: (1 error)
          <root>.level: TypeParseError: Value type not match - int expected but float found.
        >>>
        >>> u = child('level', 2) >> parent(2) >> is_type(int)
        >>> u.call(1.0)  # parent 2 levels, <root>
        argsloader.base.exception.MultipleParseError: (1 error)
          <root>: TypeParseError: Value type not match - int expected but float found.
    """
    return ParentPositionUnit(level)
