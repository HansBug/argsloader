from textwrap import dedent
from types import MethodType
from typing import Mapping, Any

import inflection
import wordninja
from hbutils.design import SingletonMark
from hbutils.reflection import fassign

from .build import CalculateUnit
from .utils import keep
from ..base import ParseError

__all__ = [
    'abs_', 'inv', 'invert', 'pos', 'neg', 'not_',
    'add', 'plus', 'sub', 'minus', 'mul', 'matmul', 'truediv', 'floordiv', 'mod',
    'pow_', 'lshift', 'rshift', 'and_', 'or_', 'band', 'bor', 'bxor',
    'eq', 'ne', 'ge', 'gt', 'le', 'lt',
]


def _nonsense():
    raise NotImplementedError  # pragma: no cover


S_ = SingletonMark('math_op_self')


def _create_unary_op(op, name_=None, funcname=None):
    short_name = (name_ or op.__name__).strip().strip('_')
    funcname = funcname or short_name

    class _UnaryOpUnit(CalculateUnit):
        __names__ = ('v1',)
        __errors__ = (ValueError, TypeError)

        def __init__(self, v1):
            CalculateUnit.__init__(self, v1)

        def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
            return op(pres['v1'])

    _UnaryOpUnit.__name__ = inflection.camelize(f'{short_name}_op_unit')
    _UnaryOpUnit.__module__ = _nonsense.__module__

    @fassign(
        __name__=funcname,
        __module__=_nonsense.__module__,
    )
    def _op_func(v1=S_) -> '_UnaryOpUnit':
        return _UnaryOpUnit(keep() if v1 is S_ else v1)

    _op_func.__doc__ = dedent(rf"""
        Overview:s
            Get the {name_} unary operation unit.
                
        :param v1: First value, default means the :func:`argsloader.units.utils.keep` will be used.
        :return: {name_.capitalize()} operation unit.
            
        Examples::
            - Simple usage
            
            >>> from argsloader.units import {funcname}
            >>> u = {funcname}()
            >>> u(10)
            {_op_func()(10)}
            >>> u(0)
            {_op_func()(0)}
            
            - Inner nested usage

            >>> u = {funcname}(lambda x: x + 2)
            >>> u(8)
            {_op_func(lambda x: x + 2)(8)}
            >>> u(-2)
            {_op_func(lambda x: x + 2)(-2)}
            
            - Prefix usage
            
            >>> u = (lambda x: x + 2) >> {funcname}()
            >>> u(8)
            {((lambda x: x + 2) >> _op_func())(8)}
            >>> u(-2)
            {((lambda x: x + 2) >> _op_func())(-2)}
    """)

    return _op_func


# math unary operation
abs_ = _create_unary_op(lambda x: abs(x), 'abs', 'abs_')
invert = _create_unary_op(lambda x: ~x, 'invert')
inv = invert
pos = _create_unary_op(lambda x: +x, 'pos')
neg = _create_unary_op(lambda x: -x, 'neg')
not_ = _create_unary_op(lambda x: not x, 'not', 'not_')


def _create_binary_op(op, name_, sign, funcname=None, reduce=False, nodoc=False):
    short_name = name_.strip().strip('_')
    funcname = funcname or short_name

    class _BinaryOpUnit(CalculateUnit):
        __names__ = ('v1', 'v2',)
        __errors__ = (ValueError, TypeError)

        def __init__(self, v1, v2):
            CalculateUnit.__init__(self, v1, v2)

        def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
            return op(pres['v1'], pres['v2'])

    _BinaryOpUnit.__name__ = inflection.camelize(f'{"_".join(wordninja.split(short_name))}_op_unit')
    _BinaryOpUnit.__module__ = _nonsense.__module__

    @fassign(
        __name__=f'{funcname.rstrip("_")}_from',
        __module__=_nonsense.__module__
    )
    def _op_func_from(self, v1) -> '_BinaryOpUnit':
        return self(v1, keep())

    @fassign(
        __name__=f'{funcname.rstrip("_")}_by',
        __module__=_nonsense.__module__
    )
    def _op_func_by(self, v2) -> '_BinaryOpUnit':
        return self(keep(), v2)

    if reduce:
        @fassign(
            __name__=funcname,
            __module__=_nonsense.__module__,
        )
        def _op_func(v1, *vs) -> '_BinaryOpUnit':
            cur = v1
            for iv in vs:
                cur = _BinaryOpUnit(cur, iv)
            return cur

        _op_func.from_ = MethodType(_op_func_from, _op_func)
        _op_func.by = MethodType(_op_func_by, _op_func)
        if not nodoc:
            _op_func.__doc__ = dedent(f"""
                Overview:
                    Get the {name_} binary operation unit.
    
                :param v1: First unit.
                :param vs: Other units, multiple units are supported.
                :return: {name_.capitalize()} operation unit.
    
                Examples::
                    - Simple usage
    
                    >>> from argsloader.units import {funcname}, keep
                    >>> u = {funcname}(keep(), 3)
                    >>> u(23)  # 23 {sign} 3
                    {_op_func(keep(), 3)(23)}
    
                    - Multiple usage

                    >>> u = {funcname}(keep(), 3, lambda x: x * 2)  # 23 {sign} 3 {sign} (23 * 2)
                    {_op_func(keep(), 3, lambda x: x * 2)(23)}
    
                    - Suffix from usage
    
                    >>> u = keep() >> {funcname}.from_(3)
                    >>> u(23)  # 3 {sign} 23
                    {(keep() >> _op_func.from_(3))(23)}
    
                    - Suffix by usage
    
                    >>> u = keep() >> {funcname}.by(3)
                    >>> u(23)  # 23 {sign} 3
                    {(keep() >> _op_func.by(3))(23)}
            """)

    else:
        @fassign(
            __name__=funcname,
            __module__=_nonsense.__module__,
        )
        def _op_func(v1, v2) -> '_BinaryOpUnit':
            return _BinaryOpUnit(v1, v2)

        _op_func.from_ = MethodType(_op_func_from, _op_func)
        _op_func.by = MethodType(_op_func_by, _op_func)
        if not nodoc:
            _op_func.__doc__ = dedent(f"""
                Overview:
                    Get the {name_} binary operation unit.
    
                :param v1: First unit.
                :param v2: Second unit.
                :return: {name_.capitalize()} operation unit.
                
                Examples::
                    - Simple usage
                    
                    >>> from argsloader.units import {funcname}, keep
                    >>> u = {funcname}(keep(), 3)
                    >>> u(23)  # 23 {sign} 3
                    {_op_func(keep(), 3)(23)}
                    
                    - Suffix from usage
                    
                    >>> u = keep() >> {funcname}.from_(3)
                    >>> u(23)  # 3 {sign} 23
                    {(keep() >> _op_func.from_(3))(23)}
                    
                    - Suffix by usage
                    
                    >>> u = keep() >> {funcname}.by(3)
                    >>> u(23)  # 23 {sign} 3
                    {(keep() >> _op_func.by(3))(23)}
            """)

    return _op_func


# math binary operation
add = _create_binary_op(lambda x, y: x + y, 'add', '+', reduce=True)
plus = add
sub = _create_binary_op(lambda x, y: x - y, 'sub', '-')
minus = sub
mul = _create_binary_op(lambda x, y: x * y, 'mul', '*', reduce=True)
matmul = _create_binary_op(lambda x, y: x @ y, 'matmul', '@', reduce=True, nodoc=True)
truediv = _create_binary_op(lambda x, y: x / y, 'truediv', '/')
floordiv = _create_binary_op(lambda x, y: x // y, 'floordiv', '//')
mod = _create_binary_op(lambda x, y: x % y, 'mod', '%')
pow_ = _create_binary_op(lambda x, y: x ** y, 'pow', '**', 'pow_')
lshift = _create_binary_op(lambda x, y: x << y, 'lshift', '<<')
rshift = _create_binary_op(lambda x, y: x >> y, 'rshift', '>>')
and_ = _create_binary_op(lambda x, y: x and y, 'and', 'and', 'and_', reduce=True)
or_ = _create_binary_op(lambda x, y: x or y, 'or', 'or', 'or_', reduce=True)
band = _create_binary_op(lambda x, y: x & y, 'band', '&', reduce=True)
bor = _create_binary_op(lambda x, y: x | y, 'bor', '|', reduce=True)
bxor = _create_binary_op(lambda x, y: x ^ y, 'bxor', '^', reduce=True)


def _binary_check_res_doc(func):
    try:
        return repr(func())
    except ParseError as err:
        return f'{type(err).__name__}: {str(err)}'


def _create_binary_check(op, name_, sign, opsign, preposition, funcname=None):
    short_name = name_.strip().strip('_')
    funcname = funcname or short_name

    class _BinaryCheckUnit(CalculateUnit):
        __names__ = ('v1', 'v2',)
        __errors__ = (ValueError, TypeError)

        def __init__(self, v1, v2):
            CalculateUnit.__init__(self, v1, v2)

        def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
            v1, v2 = pres['v1'], pres['v2']
            if not op(v1, v2):
                raise ValueError(f'Expected v1 {sign} v2, but {repr(v1)} {opsign} {repr(v2)} is found.')
            else:
                return v

    _BinaryCheckUnit.__name__ = inflection.camelize(f'{"_".join(wordninja.split(short_name))}_check_unit')
    _BinaryCheckUnit.__module__ = _nonsense.__module__

    @fassign(
        __name__=f'{funcname.rstrip("_")}_{preposition}',
        __module__=_nonsense.__module__
    )
    def _op_func_to(self, v2) -> '_BinaryCheckUnit':
        return self(keep(), v2)

    @fassign(
        __name__=funcname,
        __module__=_nonsense.__module__,
    )
    def _op_func(v1, v2) -> '_BinaryCheckUnit':
        return _BinaryCheckUnit(v1, v2)

    setattr(_op_func, preposition, MethodType(_op_func_to, _op_func))
    _op_func.__doc__ = dedent(f"""
        Overview:
            Get the {name_} binary comparison check unit.

            If ``v1 {sign} v2`` is satisfied, the inputted value will be returned without any change, \
            or ``ValueError`` will be raised.

        :param v1: First unit.
        :param v2: Second unit.
        :return: {name_.capitalize()} comparison unit.
        :raises ValueError: When comparison failed, ``ValueError`` will be raised.

        Examples::
            - Simple comparison check

            >>> from argsloader.units import {funcname}, keep
            >>> u = {funcname}(keep(), 2)
            >>> u(1)  # 1 {sign} 2
            {_binary_check_res_doc(lambda: _op_func(keep(), 2)(1))}
            >>> u(2)  # 2 {sign} 2
            {_binary_check_res_doc(lambda: _op_func(keep(), 2)(2))}
            >>> u(3)  # 3 {sign} 2
            {_binary_check_res_doc(lambda: _op_func(keep(), 2)(3))}

            - Suffix check

            >>> u = (lambda x: x * 2) >> {funcname}.{preposition}(2)
            >>> u(0)  # (0 * 2) {sign} 2
            {_binary_check_res_doc(lambda: ((lambda x: x * 2) >> getattr(_op_func, preposition)(2))(0))}
            >>> u(1)  # (1 * 2) {sign} 2
            {_binary_check_res_doc(lambda: ((lambda x: x * 2) >> getattr(_op_func, preposition)(2))(1))}
            >>> u(2)  # (2 * 2) {sign} 2
            {_binary_check_res_doc(lambda: ((lambda x: x * 2) >> getattr(_op_func, preposition)(2))(2))}
    """)

    return _op_func


# logic binary operation
eq = _create_binary_check(lambda x, y: x == y, 'eq', '==', '!=', 'to_')
ne = _create_binary_check(lambda x, y: x != y, 'ne', '!=', '==', 'to_')
le = _create_binary_check(lambda x, y: x <= y, 'le', '<=', '>', 'than')
lt = _create_binary_check(lambda x, y: x < y, 'lt', '<', '>=', 'than')
ge = _create_binary_check(lambda x, y: x >= y, 'ge', '>=', '<', 'than')
gt = _create_binary_check(lambda x, y: x > y, 'gt', '>', '<=', 'than')
