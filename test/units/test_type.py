import pytest

from argsloader.base import ParseError, PValue
from argsloader.units import is_type, to_type, is_subclass


class _DemoType:
    pass


@pytest.mark.unittest
class TestUnitsType:
    def test_is_type(self):
        it = is_type(int)
        assert it(1) == 1
        assert it(2) == 2

        with pytest.raises(ParseError) as ei:
            _ = it(2.0)

        err = ei.value
        assert isinstance(err, TypeError)
        assert isinstance(err, ParseError)
        assert err.message == 'Value type not match - int expected but float found.'
        assert err.unit is it
        assert err.value == PValue(2.0, ())
        assert err.info == ()

    def test_is_type_with_tuple(self):
        it = is_type((int, float))
        assert it(1) == 1
        assert it(2) == 2
        assert it(2.0) == 2.0

        with pytest.raises(ParseError) as ei:
            _ = it('2.0')

        err = ei.value
        assert isinstance(err, TypeError)
        assert isinstance(err, ParseError)
        assert err.message == 'Value type not match - (int, float) expected but str found.'
        assert err.unit is it
        assert err.value == PValue('2.0', ())
        assert err.info == ()

        itx = is_type(_DemoType)
        with pytest.raises(ParseError) as ei:
            _ = itx(None)

        err = ei.value
        assert isinstance(err, TypeError)
        assert isinstance(err, ParseError)
        assert err.message == 'Value type not match - test.units.test_type._DemoType expected but NoneType found.'
        assert err.unit is itx
        assert err.value == PValue(None, ())
        assert err.info == ()

    def test_to_type(self):
        ot = to_type(int)
        assert ot(1) == 1
        assert ot('1') == 1
        assert ot(1.5) == int(1.5)

        with pytest.raises(ParseError) as ei:
            _ = ot('1.5')

        err = ei.value
        assert isinstance(err, ValueError)
        assert isinstance(err, ParseError)
        assert 'invalid literal' in err.message
        assert err.unit is ot
        assert err.value == PValue('1.5', ())
        assert err.info == ()

    def test_is_subclass(self):
        class A(_DemoType):
            pass

        u = is_subclass(_DemoType)
        assert u(A) is A
        assert u(_DemoType) is _DemoType

        with pytest.raises(ParseError) as ei:
            u(str)

        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, TypeError)

        with pytest.raises(ParseError) as ei:
            u(1)

        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, TypeError)
