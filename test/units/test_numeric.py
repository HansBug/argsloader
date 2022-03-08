import math
from textwrap import dedent

import pytest

from argsloader.base import ParseError
from argsloader.units import interval, add, number


# noinspection DuplicatedCode,PyPep8Naming,PyUnresolvedReferences
@pytest.mark.unittest
class TestUnitsNumeric:
    def test_interval_lr(self):
        u = interval.lr(3, 10)
        assert u(4) == 4
        assert u(8.5) == 8.5
        with pytest.raises(ParseError) as ei:
            u(3)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert '(3, 10)' in err.message

        with pytest.raises(ParseError) as ei:
            u(10)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert '(3, 10)' in err.message

        with pytest.raises(ParseError) as ei:
            u(-1)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert '(3, 10)' in err.message

    def test_interval_Lr(self):
        u = interval.Lr(3, 10)
        assert u(4) == 4
        assert u(8.5) == 8.5
        assert u(3) == 3
        with pytest.raises(ParseError) as ei:
            u(10)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert '[3, 10)' in err.message

        with pytest.raises(ParseError) as ei:
            u(-1)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert '[3, 10)' in err.message

    def test_interval_lR(self):
        u = interval.lR(3, 10)
        assert u(4) == 4
        assert u(8.5) == 8.5
        with pytest.raises(ParseError) as ei:
            u(3)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert '(3, 10]' in err.message

        assert u(10) == 10

        with pytest.raises(ParseError) as ei:
            u(-1)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert '(3, 10]' in err.message

    def test_interval_LR(self):
        u = interval.LR(3, 10)
        assert u(4) == 4
        assert u(8.5) == 8.5
        assert u(3) == 3
        assert u(10) == 10

        with pytest.raises(ParseError) as ei:
            u(-1)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert '[3, 10]' in err.message

    def test_interval_l(self):
        u = interval.l(3)
        assert u(4) == 4
        assert u(8.5) == 8.5

        with pytest.raises(ParseError) as ei:
            u(3)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert '(3, +inf]' in err.message

        assert u(10) == 10
        assert u(+math.inf) == +math.inf

        with pytest.raises(ParseError) as ei:
            u(-math.inf)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert '(3, +inf]' in err.message

        with pytest.raises(ParseError) as ei:
            u(-1)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert '(3, +inf]' in err.message

    def test_interval_L(self):
        u = interval.L(3)
        assert u(4) == 4
        assert u(8.5) == 8.5
        assert u(3) == 3
        assert u(10) == 10
        assert u(+math.inf) == +math.inf

        with pytest.raises(ParseError) as ei:
            u(-math.inf)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert '[3, +inf]' in err.message

        with pytest.raises(ParseError) as ei:
            u(-1)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert '[3, +inf]' in err.message

    def test_interval_r(self):
        u = interval.r(10)
        assert u(4) == 4
        assert u(8.5) == 8.5
        assert u(3) == 3

        with pytest.raises(ParseError) as ei:
            u(10)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert '[-inf, 10)' in err.message

        with pytest.raises(ParseError) as ei:
            u(+math.inf)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert '[-inf, 10)' in err.message

        assert u(-math.inf) == -math.inf
        assert u(-1) == -1

    def test_interval_R(self):
        u = interval.R(10)
        assert u(4) == 4
        assert u(8.5) == 8.5
        assert u(3) == 3
        assert u(10) == 10

        with pytest.raises(ParseError) as ei:
            u(+math.inf)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert '[-inf, 10]' in err.message

        assert u(-math.inf) == -math.inf
        assert u(-1) == -1

    def test_interval_float_number(self):
        u = interval.R(10.6543210101)
        assert u(4) == 4
        assert u(8.5) == 8.5
        assert u(3) == 3
        assert u(10) == 10

        with pytest.raises(ParseError) as ei:
            u(+math.inf)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert '[-inf, 10.6543]' in err.message

    def test_interval_syntax(self):
        with pytest.raises(SyntaxError):
            interval(1)
        with pytest.raises(SyntaxError):
            interval >> add.by(2)

        assert repr(interval).strip() == dedent("""
            <(X)_IntervalProxy>
        """).strip()

    def test_interval_complex(self):
        u = interval.R(0.87323232).Lr(3, 10).l(15.2)
        assert u(4) == 4
        assert u(8.5) == 8.5
        assert u(3) == 3

        with pytest.raises(ParseError) as ei:
            u(10)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert '[-inf, 0.8732] | [3, 10) | (15.2000, +inf]'

        with pytest.raises(ParseError) as ei:
            u(0.9)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert '[-inf, 0.8732] | [3, 10) | (15.2000, +inf]'

        assert u(0.5) == 0.5
        assert u(+math.inf) == +math.inf
        assert u(-math.inf) == -math.inf

    def test_number(self):
        u = number()
        assert u(1) == 1
        assert u(1.5) == 1.5
        assert u('1.5') == 1.5
        assert u('92348') == 92348
        assert u('0x92348F') == 0x92348f
        assert u('0X92348f') == 0x92348f
        assert u('0o236745') == 0o236745
        assert u('0O236745') == 0o236745
        assert u('0b010100110111') == 0b010100110111
        assert u('0B010100110111') == 0b010100110111

        with pytest.raises(ParseError) as ei:
            u('abcdef')
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ("Unrecognized value format - 'abcdef'.",)

        with pytest.raises(ParseError) as ei:
            u(None)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, TypeError)
        assert err.args == ('Value type not match - int, float or str expected but NoneType found.',)
