from types import MethodType
from typing import Mapping, Any

import inflection
import wordninja
from hbutils.design import SingletonMark
from hbutils.reflection import fassign

from .base import CalculateUnit
from .utils import keep

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
    funcname = short_name or funcname

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
        __module__=_nonsense.__module__
    )
    def _op_func(v1=S_) -> '_UnaryOpUnit':
        return _UnaryOpUnit(keep() if v1 is S_ else v1)

    return _op_func


# math unary operation
abs_ = _create_unary_op(lambda x: abs(x), 'abs', 'abs_')
invert = _create_unary_op(lambda x: ~x, 'invert')
inv = invert
pos = _create_unary_op(lambda x: +x, 'pos')
neg = _create_unary_op(lambda x: -x, 'neg')
not_ = _create_unary_op(lambda x: not x, 'not', 'not_')


def _create_binary_op(op, name_, funcname=None, reduce=False):
    short_name = name_.strip().strip('_')
    funcname = short_name or funcname

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

    @fassign(
        __name__=funcname,
        __module__=_nonsense.__module__,
    )
    def _op_func(v1, *vs) -> '_BinaryOpUnit':
        if reduce:
            cur = v1
            for iv in vs:
                cur = _BinaryOpUnit(cur, iv)
            return cur
        else:
            return _BinaryOpUnit(v1, *vs)

    _op_func.from_ = MethodType(_op_func_from, _op_func)
    _op_func.by = MethodType(_op_func_by, _op_func)

    return _op_func


# math binary operation
add = _create_binary_op(lambda x, y: x + y, 'add', reduce=True)
plus = add
sub = _create_binary_op(lambda x, y: x - y, 'sub')
minus = sub
mul = _create_binary_op(lambda x, y: x * y, 'mul', reduce=True)
matmul = _create_binary_op(lambda x, y: x @ y, 'matmul', reduce=True)
truediv = _create_binary_op(lambda x, y: x / y, 'truediv')
floordiv = _create_binary_op(lambda x, y: x // y, 'floordiv')
mod = _create_binary_op(lambda x, y: x % y, 'mod')
pow_ = _create_binary_op(lambda x, y: x ** y, 'pow', 'pow_')
lshift = _create_binary_op(lambda x, y: x << y, 'lshift')
rshift = _create_binary_op(lambda x, y: x >> y, 'rshift')
and_ = _create_binary_op(lambda x, y: x and y, 'and', 'and_', reduce=True)
or_ = _create_binary_op(lambda x, y: x or y, 'or', 'or_', reduce=True)
band = _create_binary_op(lambda x, y: x & y, 'band', reduce=True)
bor = _create_binary_op(lambda x, y: x | y, 'bor', reduce=True)
bxor = _create_binary_op(lambda x, y: x ^ y, 'bxor', reduce=True)


def _create_binary_check(op, name_, sign, opsign, preposition, funcname=None):
    short_name = name_.strip().strip('_')
    funcname = short_name or funcname

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
    def _op_func(v1, *vs) -> '_BinaryCheckUnit':
        return _BinaryCheckUnit(v1, *vs)

    setattr(_op_func, preposition, MethodType(_op_func_to, _op_func))

    return _op_func


# logic binary operation
eq = _create_binary_check(lambda x, y: x == y, 'eq', '==', '!=', 'to_')
ne = _create_binary_check(lambda x, y: x != y, 'ne', '!=', '==', 'to_')
le = _create_binary_check(lambda x, y: x <= y, 'le', '<=', '>', 'than')
lt = _create_binary_check(lambda x, y: x < y, 'lt', '<', '>=', 'than')
ge = _create_binary_check(lambda x, y: x >= y, 'ge', '>=', '<', 'than')
gt = _create_binary_check(lambda x, y: x > y, 'gt', '>', '<=', 'than')
