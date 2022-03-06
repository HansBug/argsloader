from typing import Mapping, Any

from .base import CalculateUnit


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
    __names__ = ('type',)
    __errors__ = (TypeError,)

    def __init__(self, type_):
        CalculateUnit.__init__(self, type_)

    def _calculate(self, v, pres):
        type_ = pres['type']
        # noinspection PyTypeHints
        if isinstance(v, type_):
            return v
        else:
            raise TypeError(f'Value type not match - {_tname(type_)} expected but {_tname(type(v))} found.')


def is_type(type_) -> IsTypeUnit:
    return IsTypeUnit(type_)


class ToTypeUnit(CalculateUnit):
    __names__ = ('type',)
    __errors__ = (TypeError, ValueError)

    def __init__(self, type_):
        CalculateUnit.__init__(self, type_)

    def _calculate(self, v, pres) -> object:
        type_: type = pres['type']
        return type_(v)


def to_type(type_) -> ToTypeUnit:
    return ToTypeUnit(type_)


class IsSubclassUnit(CalculateUnit):
    __names__ = ('type',)
    __errors__ = (TypeError,)

    def __init__(self, type_):
        CalculateUnit.__init__(self, type_)

    def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
        type_: type = pres['type']
        # noinspection PyTypeHints,PyTypeChecker
        if issubclass(v, type_):
            return v
        else:
            raise TypeError(f'Value type not match - {_tname(type_)}\'s subclass expected but {_tname(type(v))} found.')


def is_subclass(type_) -> IsSubclassUnit:
    return is_type(type) >> IsSubclassUnit(type_)
