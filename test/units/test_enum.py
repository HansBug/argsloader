from enum import Enum, Flag
from textwrap import dedent

import pytest
from hbutils.model import AutoIntEnum

from argsloader.base import ParseError
from argsloader.units import enum


@pytest.mark.unittest
class TestUnitsEnum:
    def test_enum_with_enum(self):
        class Ex(Enum):
            A = 'a1'
            B = 'b2'

        u = enum(Ex)
        assert u(Ex.A) == Ex.A
        assert u(Ex.B) == Ex.B

        assert u('A') == Ex.A
        assert u('a') == Ex.A
        assert u('B') == Ex.B
        assert u('b') == Ex.B
        assert u('  b  ') == Ex.B
        with pytest.raises(ParseError) as ei:
            u('C')
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ("Value is expected to be a Ex object, but 'C' found actually.",)

        assert u('a1') == Ex.A
        assert u('b2') == Ex.B
        with pytest.raises(ParseError) as ei:
            u('A1')
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ("Value is expected to be a Ex object, but 'A1' found actually.",)

        assert repr(u).strip() == dedent("""
            <EnumUnit enum: <enum 'Ex'>>
        """).strip()

    def test_enum_invalid(self):
        with pytest.raises(TypeError) as ei:
            enum(int)
        err = ei.value
        assert isinstance(err, TypeError)
        assert not isinstance(err, ParseError)

    def test_enum_auto_int_enum(self):
        class MyIntEnum(AutoIntEnum):
            def __init__(self, k):
                self._k = k

            FIRST_VAL = 'f v v'
            SECOND_VAL = 's n v'
            THIRD_VAL = 'tvf'

        u = enum(MyIntEnum)
        assert u(MyIntEnum.FIRST_VAL) == MyIntEnum.FIRST_VAL
        assert u(MyIntEnum.SECOND_VAL) == MyIntEnum.SECOND_VAL
        assert u(MyIntEnum.THIRD_VAL) == MyIntEnum.THIRD_VAL

        assert u('FIRST_VAL') == MyIntEnum.FIRST_VAL
        assert u('first_val') == MyIntEnum.FIRST_VAL
        assert u('FirstVal') == MyIntEnum.FIRST_VAL
        assert u('SecondVal') == MyIntEnum.SECOND_VAL
        assert u('third_val') == MyIntEnum.THIRD_VAL
        with pytest.raises(ParseError) as ei:
            u('fourth_val')
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ("Value is expected to be a MyIntEnum object, but 'fourth_val' found actually.",)

        assert u(1) == MyIntEnum.FIRST_VAL
        assert u(2) == MyIntEnum.SECOND_VAL
        assert u(3) == MyIntEnum.THIRD_VAL
        with pytest.raises(ParseError) as ei:
            u(4)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ("Value is expected to be a MyIntEnum object, but 4 found actually.",)

    def test_enum_with_flag(self):
        class CFlag(Flag):
            R = 1
            G = 2
            B = 4
            W = R | G | B

        u = enum(CFlag)
        assert u(CFlag.R) == CFlag.R
        assert u(CFlag.G) == CFlag.G
        assert u(CFlag.B) == CFlag.B
        assert u(CFlag.W) == CFlag.W
        assert u(CFlag(6)) == CFlag.G | CFlag.B

        assert u('r') == CFlag.R
        assert u('G') == CFlag.G
        assert u('b') == CFlag.B
        assert u('r,g') == CFlag.R | CFlag.G
        assert u('r g b') == CFlag.W
        assert u('w') == CFlag.W
        assert u('') == CFlag(0)
        assert u('1 r,g') == CFlag.R | CFlag.G

        assert u([1, 4]) == CFlag.R | CFlag.B
        assert u((2, 'b')) == CFlag.G | CFlag.B
        assert u({'R', 2}) == CFlag.R | CFlag.G
        assert u([1]) == CFlag.R
        assert u([]) == CFlag(0)
        assert u({1, 'g', 'B'}) == CFlag.W
        assert u({5, 2}) == CFlag.W
