from functools import wraps
from types import FunctionType, BuiltinFunctionType, MethodType, BuiltinMethodType, LambdaType
from typing import Mapping, Any

import inflection
from hbutils.reflection import frename

from .base import raw
from .build import CalculateUnit

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
    """
    Overview:
        Unit for do processing.
    """
    __names__ = ('func',)

    def __init__(self, f):
        """
        Constructor of :class:`ProcUnit`.

        :param f: Processor function.
        """
        if isinstance(f, _FUNC_TYPES):
            f = raw(f)
        CalculateUnit.__init__(self, f)

    def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
        return pres['func'](v)


def proc(f) -> ProcUnit:
    """
    Overview:
        Wrap a processor function to unit.

    :param f: Processor function.
    :return: A processor unit.

    Examples::
        - Use defined function

        >>> from argsloader.units import proc
        >>> u = proc(lambda x: x ** 2)
        >>> u(2)
        4
        >>> u(10)
        100

        - Use native function

        >>> u = proc(str.upper)
        >>> u('word')
        'WORD'
        >>> u('this is message')
        'THIS IS MESSAGE'

        - Native support in unit calculation

        >>> from argsloader.units import add
        >>> u = add.by(2) >> (lambda x: x ** 2)
        >>> u(10)
        144
        >>> u(20)
        484

    .. warning::
        - Only simple processor function is supported, which is like ``lambda x: None``.

        - Please **make sure no error will be raised in the processor function**.

    """
    return ProcUnit(f)


def ufunc(errors=()):
    """
    Overview:
        Wrap a function to unit supported function.

    :param errors: Errors need to be processed.
    :return: A wrapped function unit.

    Examples::
        >>> import math
        >>> from argsloader.units import ufunc, add, sub, keep
        >>> @ufunc(errors=(ValueError,))  # this is necessary, or this error will not be recorded
        ... def myfunc(a, b, c):
        ...     p = (a + b + c) / 2
        ...     try:
        ...         return math.sqrt(p * (p - a) * (p - b) * (p - c))
        ...     except ValueError:
        ...         raise ValueError(f'Invalid triangle - ({a}, {b}, {c}).')
        ...
        >>> u = myfunc(add.by(2), sub.by(2), keep())
        >>> u(10)  # area of triangle (12, 8, 10)
        39.68626966596886
        >>> u(3)  # area of triangle (5, 1, 3)
        ValueParseError: Invalid triangle - (5, 1, 3).

    """

    def _decorator(func):
        class _NewFuncUnit(CalculateUnit):
            __names__ = ('args', 'kwargs')
            __errors__ = errors

            def __init__(self, *args, **kwargs):
                CalculateUnit.__init__(self, args, kwargs)

            def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
                return func(*pres['args'], **pres['kwargs'])

        _NewFuncUnit.__name__ = inflection.camelize(f'{func.__name__.strip("_")}_func_unit')
        _NewFuncUnit.__module__ = func.__module__

        @frename(inflection.underscore(f'u_{func.__name__.lstrip("_")}'))
        @wraps(func)
        def _new_func(*args, **kwargs) -> _NewFuncUnit:
            return _NewFuncUnit(*args, **kwargs)

        return _new_func

    return _decorator
