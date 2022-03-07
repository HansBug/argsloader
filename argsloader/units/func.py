from functools import wraps
from types import FunctionType, BuiltinFunctionType, MethodType, BuiltinMethodType, LambdaType
from typing import Mapping, Any

import inflection
from hbutils.reflection import fassign

from .base import CalculateUnit, raw

try:
    from types import MethodWrapperType, MethodDescriptorType, ClassMethodDescriptorType, WrapperDescriptorType
except ImportError:
    WrapperDescriptorType = type(object.__init__)
    MethodWrapperType = type(object().__str__)
    MethodDescriptorType = type(str.join)
    ClassMethodDescriptorType = type(dict.__dict__['fromkeys'])

_FUNC_TYPES = (
    FunctionType, BuiltinFunctionType, LambdaType,
    MethodType, BuiltinMethodType, MethodWrapperType,
    MethodDescriptorType, ClassMethodDescriptorType, WrapperDescriptorType
)


def _nonsense():
    raise NotImplementedError  # pragma: no cover


class ProcUnit(CalculateUnit):
    __names__ = ('func',)

    def __init__(self, f):
        if isinstance(f, _FUNC_TYPES):
            f = raw(f)
        CalculateUnit.__init__(self, f)

    def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
        return pres['func'](v)


def proc(f) -> ProcUnit:
    return ProcUnit(f)


def ufunc(errors=()):
    def _decorator(func):
        class _NewFuncUnit(CalculateUnit):
            __names__ = ('args', 'kwargs')
            __errors__ = errors

            def __init__(self, *args, **kwargs):
                CalculateUnit.__init__(self, args, kwargs)

            def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
                return func(*pres['args'], **pres['kwargs'])

        _NewFuncUnit.__name__ = inflection.camelize(f'{func.__name__}_func_unit')
        _NewFuncUnit.__module__ = func.__module__

        @fassign(
            __name__=inflection.underscore(f'u_{func.__name__}'),
            __module__=func.__module__,
        )
        @wraps(func)
        def _new_func(*args, **kwargs) -> _NewFuncUnit:
            return _NewFuncUnit(*args, **kwargs)

        return _new_func

    return _decorator
