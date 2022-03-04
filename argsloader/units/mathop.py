from typing import Mapping, Any

import inflection
import wordninja
from hbutils.design import SingletonMark
from hbutils.reflection import fassign

from .base import _CalculateUnit
from .utils import keep

__all__ = [
    'abs_', 'inv', 'invert', 'pos', 'neg', 'not_',
    'add', 'plus', 'sub', 'minus', 'mul', 'matmul', 'truediv', 'floordiv', 'mod',
    'pow_', 'lshift', 'rshift', 'and_', 'or_', 'band', 'bor', 'bxor',
    'eq', 'ne', 'ge', 'gt', 'le', 'lt', 'in_',
]


def _nonsense():
    raise NotImplementedError  # pragma: no cover


S_ = SingletonMark('math_op_self')


def _create_unary_op(op, name_=None, funcname=None):
    short_name = (name_ or op.__name__).strip().strip('_')
    funcname = short_name or funcname

    class _UnaryOpUnit(_CalculateUnit):
        __names__ = ('v1',)
        __errors__ = (ValueError, TypeError)

        def __init__(self, v1):
            _CalculateUnit.__init__(self, v1)

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

# logic unary operation
# TODO: add support for logical unary operation
not_ = _create_unary_op(lambda x: not x, 'not', 'not_')


def _create_binary_op(op, name_, funcname=None, reduce=False):
    short_name = name_.strip().strip('_')
    funcname = short_name or funcname

    class _BinaryOpUnit(_CalculateUnit):
        __names__ = ('v1', 'v2',)
        __errors__ = (ValueError, TypeError)

        def __init__(self, v1, v2):
            _CalculateUnit.__init__(
                self,
                keep() if v1 is S_ else v1,
                keep() if v2 is S_ else v2,
            )

        def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
            return op(pres['v1'], pres['v2'])

    _BinaryOpUnit.__name__ = inflection.camelize(f'{"_".join(wordninja.split(short_name))}_op_unit')
    _BinaryOpUnit.__module__ = _nonsense.__module__

    @fassign(
        __name__=f'{funcname.rstrip("_")}_from',
        __module__=_nonsense.__module__
    )
    def _op_func_from(v1) -> '_BinaryOpUnit':
        return _BinaryOpUnit(v1, S_)

    @fassign(
        __name__=f'{funcname.rstrip("_")}_by',
        __module__=_nonsense.__module__
    )
    def _op_func_by(v2) -> '_BinaryOpUnit':
        return _BinaryOpUnit(S_, v2)

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

    _op_func.from_ = _op_func_from
    _op_func.by = _op_func_by

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
band = _create_binary_op(lambda x, y: x & y, 'band', reduce=True)
bor = _create_binary_op(lambda x, y: x | y, 'bor', reduce=True)
bxor = _create_binary_op(lambda x, y: x ^ y, 'bxor', reduce=True)

# logic binary operation
# TODO: add support for logical binary operation
eq = _create_binary_op(lambda x, y: x == y, 'eq')
ne = _create_binary_op(lambda x, y: x != y, 'ne')
le = _create_binary_op(lambda x, y: x <= y, 'le')
lt = _create_binary_op(lambda x, y: x < y, 'lt')
ge = _create_binary_op(lambda x, y: x >= y, 'ge')
gt = _create_binary_op(lambda x, y: x > y, 'gt')
and_ = _create_binary_op(lambda x, y: x and y, 'and', 'and_', reduce=True)
or_ = _create_binary_op(lambda x, y: x or y, 'or', 'or_', reduce=True)
in_ = _create_binary_op(lambda x, y: x in y, 'in', 'in_')
