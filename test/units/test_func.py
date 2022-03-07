import pytest
from inflection import humanize

from argsloader.base import ParseError
from argsloader.units import proc, keep, ufunc, add, mul


@pytest.mark.unittest
class TestUnitsFunc:
    def test_proc(self):
        # FunctionType, LambdaType
        u = proc(lambda x: x.upper())
        assert u('abc') == 'ABC'

        # BuiltinFunctionType, BuiltinMethodType
        u = proc(len)
        assert u('abc') == 3

        # MethodType
        class V:
            def __init__(self, v):
                self.v = v

            def append(self, x):
                self.v.append(x)
                return self.v

        ls = V([])
        u = proc(ls.append)
        assert u('abc') == ['abc']
        assert ls.v == ['abc']

        # MethodDescriptorType
        u = proc(str.upper)
        assert u('abc') == 'ABC'

        # WrapperDescriptorType
        u = proc(float.__str__)
        assert u(1.5) == '1.5'

        # MethodWrapperType
        num = 233
        u = proc(num.__add__)
        assert u(1) == 234

        # ClassMethodDescriptorType
        u = proc(dict.fromkeys)
        assert u('a') == {'a': None}

    def test_proc_chain(self):
        u = keep() >> humanize >> str.capitalize >> (lambda x: f"{x}.")
        assert u('this_is_a_message') == 'This is a message.'

    def test_ufunc(self):
        def _nonsense():
            pass

        @ufunc((ValueError,))
        def my_func(x, y):
            if x + y < 0:
                raise ValueError('this is the bullshit-liked message', x, y)
            else:
                return x + 2 * y

        assert my_func.__name__ == 'u_my_func'
        assert my_func.__module__ == _nonsense.__module__

        u = my_func(keep(), add.by(2) >> mul.by(3))
        ucls = type(u)
        assert ucls.__name__ == 'MyFuncFuncUnit'
        assert ucls.__module__ == _nonsense.__module__

        assert u(23) == 173
        with pytest.raises(ParseError) as ei:
            u(-10)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ('this is the bullshit-liked message', -10, -24)
