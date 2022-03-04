from typing import Mapping, Any

import inflection
import wordninja
from hbutils.design import SingletonMark
from hbutils.reflection import fassign

from .base import _CalculateUnit
from .utils import keep

__all__ = [
    'abs_', 'inv', 'invert', 'pos', 'neg', 'lnot',
    'add', 'plus', 'sub', 'minus', 'mul', 'matmul', 'truediv', 'floordiv', 'mod',
    'pow_', 'lshift', 'rshift', 'land', 'lor', 'and_', 'or_', 'xor',
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


abs_ = _create_unary_op(lambda x: abs(x), 'abs', 'abs_')
invert = _create_unary_op(lambda x: ~x, 'invert')
inv = invert
pos = _create_unary_op(lambda x: +x, 'pos')
neg = _create_unary_op(lambda x: -x, 'neg')
lnot = _create_unary_op(lambda x: not x, 'lnot')


def _create_binary_op(op, name_, funcname=None):
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
    def _op_func(v1, v2) -> '_BinaryOpUnit':
        return _BinaryOpUnit(v1, v2)

    _op_func.from_ = _op_func_from
    _op_func.by = _op_func_by

    return _op_func


add = _create_binary_op(lambda x, y: x + y, 'add')
plus = add
sub = _create_binary_op(lambda x, y: x - y, 'sub')
minus = sub
mul = _create_binary_op(lambda x, y: x * y, 'mul')
matmul = _create_binary_op(lambda x, y: x @ y, 'matmul')
truediv = _create_binary_op(lambda x, y: x / y, 'truediv')
floordiv = _create_binary_op(lambda x, y: x // y, 'floordiv')
mod = _create_binary_op(lambda x, y: x % y, 'mod')
pow_ = _create_binary_op(lambda x, y: x ** y, 'pow', 'pow_')
lshift = _create_binary_op(lambda x, y: x << y, 'lshift')
rshift = _create_binary_op(lambda x, y: x >> y, 'rshift')
land = _create_binary_op(lambda x, y: x and y, 'land')
lor = _create_binary_op(lambda x, y: x or y, 'lor')
and_ = _create_binary_op(lambda x, y: x & y, 'and', 'and_')
or_ = _create_binary_op(lambda x, y: x | y, 'or', 'or_')
xor = _create_binary_op(lambda x, y: x ^ y, 'xor', 'xor_')
