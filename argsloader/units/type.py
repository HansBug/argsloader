from .base import _CalculateUnit


def _type_full_name(type_: type) -> str:
    try:
        module_name = type_.__module__
    except AttributeError:
        module_name = None

    if module_name is not None:
        return type_.__name__
    else:
        return f'{module_name}.{type_.__name__}'


def _tname(type_) -> str:
    if isinstance(type_, type):
        return _type_full_name(type_)
    else:
        return '(' + ', '.join(map(_type_full_name, type_)) + ')'


class IsTypeUnit(_CalculateUnit):
    __names__ = ('type',)
    __errors__ = (TypeError,)

    def __init__(self, type_):
        _CalculateUnit.__init__(self, type_)

    def _calculate(self, v, pres):
        type_ = pres['type']
        # noinspection PyTypeHints
        if isinstance(v, type_):
            return v
        else:
            raise TypeError(f'Value type not match - {_tname(type_)} expected but {_tname(type(v))} found.')


def is_type(type_) -> IsTypeUnit:
    return IsTypeUnit(type_)


class ToTypeUnit(_CalculateUnit):
    __names__ = ('type',)
    __errors__ = (TypeError, ValueError)

    def __init__(self, type_):
        _CalculateUnit.__init__(self, type_)

    def _calculate(self, v, pres) -> object:
        type_: type = pres['type']
        return type_(v)


def to_type(type_) -> ToTypeUnit:
    return ToTypeUnit(type_)
