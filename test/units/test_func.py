import pytest
from inflection import humanize

from argsloader.units import proc, keep


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
