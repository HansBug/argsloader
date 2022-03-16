from typing import Mapping, Any

from .build import CalculateUnit


def _type_full_name(type_: type) -> str:
    module_name = type_.__module__
    if module_name and module_name != 'builtins':
        return f'{module_name}.{type_.__qualname__}'
    else:
        return type_.__qualname__


def _tname(type_) -> str:
    if isinstance(type_, type):
        return _type_full_name(type_)
    else:
        return '(' + ', '.join(map(_type_full_name, type_)) + ')'


class IsTypeUnit(CalculateUnit):
    """
    Overview:
        Unit for checking the data's type.
    """
    __names__ = ('type',)
    __errors__ = (TypeError,)

    def __init__(self, type_):
        """
        Constructor of :class:`IsTypeUnit`.

        :param type_: Type unit.
        """
        CalculateUnit.__init__(self, type_)

    def _calculate(self, v, pres):
        type_ = pres['type']
        # noinspection PyTypeHints
        if isinstance(v, type_):
            return v
        else:
            raise TypeError(f'Value type not match - {_tname(type_)} expected but {_tname(type(v))} found.')


def is_type(type_) -> IsTypeUnit:
    """
    Overview:
        Check if the input data is an instance of the given type.

    :param type_: Type or type unit.
    :return: A is-type unit object.

    Examples::
        >>> from argsloader.units import is_type
        >>> u = is_type(int)
        >>> u(1)
        1
        >>> u(1.0)
        TypeParseError: Value type not match - int expected but float found.
    """
    return IsTypeUnit(type_)


class ToTypeUnit(CalculateUnit):
    """
    Overview:
        Unit for transforming the input data to the given type.
    """
    __names__ = ('type',)
    __errors__ = (TypeError, ValueError)

    def __init__(self, type_):
        """
        Constructor of :class:`ToTypeUnit`.

        :param type_: Type unit.
        """
        CalculateUnit.__init__(self, type_)

    def _calculate(self, v, pres) -> object:
        type_: type = pres['type']
        return type_(v)


def to_type(type_) -> ToTypeUnit:
    """
    Overview:
        Turn the input data to the given type.

    :param type_: Type or type unit.
    :return: A to-type unit object.

    Examples::
        >>> from argsloader.units import to_type
        >>> u = to_type(int)
        >>> u(1)
        1
        >>> u(1.2)
        1
    """
    return ToTypeUnit(type_)


class IsSubclassUnit(CalculateUnit):
    """
    Overview:
        Unit for checking if the object is subclass of the given type.
    """
    __names__ = ('type',)
    __errors__ = (TypeError,)

    def __init__(self, type_):
        """
        Constructor of :class:`IsSubclassUnit`.

        :param type_: Type unit.
        """
        CalculateUnit.__init__(self, type_)

    def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
        type_: type = pres['type']
        # noinspection PyTypeHints,PyTypeChecker
        if issubclass(v, type_):
            return v
        else:
            raise TypeError(f'Value type not match - {_tname(type_)}\'s subclass expected but {_tname(type(v))} found.')


def is_subclass(type_) -> IsSubclassUnit:
    """
    Overview:
        Check if the input is a subclass of the given ``type_``.

    :param type_: Type unit.
    :return: A is-subclass unit object.

    Examples::
        >>> from argsloader.units import is_subclass
        >>> class A(dict): pass
        ...
        >>> u = is_subclass(dict)
        >>> u(dict)
        <class 'dict'>
        >>> u(A)
        <class '__main__.A'>
        >>> u(int)
        TypeParseError: Value type not match - dict's subclass expected but type found.
    """
    return is_type(type) >> IsSubclassUnit(type_)
