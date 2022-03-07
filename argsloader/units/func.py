from types import FunctionType, BuiltinFunctionType, MethodType, BuiltinMethodType, LambdaType
from typing import Mapping, Any

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


class ProcUnit(CalculateUnit):
    __names__ = ('func',)

    def __init__(self, func):
        if isinstance(func, _FUNC_TYPES):
            func = raw(func)
        CalculateUnit.__init__(self, func)

    def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
        return pres['func'](v)


def proc(func) -> ProcUnit:
    return ProcUnit(func)
