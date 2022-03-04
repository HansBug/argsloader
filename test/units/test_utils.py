import pytest

from argsloader.base import ParseError
from argsloader.units import keep, check, is_type, to_type, validity, error, template, not_, validate, add


@pytest.mark.unittest
class TestUnitsUtils:
    def test_keep(self):
        k = keep()
        assert k(2) == 2
        assert k(None) is None

        l = [1, 2, 3]
        assert k(l) is l

    def test_keep_singleton(self):
        assert keep() is keep()

    def test_check(self):
        ck = check(is_type((float, int)) >> to_type(int))
        assert ck(1) == 1
        assert ck(1.3) == 1.3

        with pytest.raises(ParseError) as ei:
            ck('sdjf')

        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, TypeError)

    def test_validity(self):
        u = validity(is_type(int) | is_type(str))
        assert u(1)
        assert not u(1.0)
        assert u('sdkjf')

    def test_error(self):
        class MyTypeError(TypeError):
            pass

        u = error(not_(validity(is_type(int) | is_type(str))), MyTypeError, '234', 5, 6)
        assert u(1) == 1
        assert u('skdjflk') == 'skdjflk'
        with pytest.raises(ParseError) as ei:
            u(1.0)

        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, MyTypeError)
        assert err.args == ('234', 5, 6)

        u = error(not_(validity(is_type(int) | is_type(str))), MyTypeError,
                  template('${V} is invalid', dict(V=keep())), 5, 6)
        assert u(1) == 1
        assert u('skdjflk') == 'skdjflk'
        with pytest.raises(ParseError) as ei:
            u(1.0)

        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, MyTypeError)
        assert err.args == ('1.0 is invalid', 5, 6)

    def test_validate(self):
        class MyTypeError(TypeError):
            pass

        u = validate(add.by(2), validity(is_type(int)), MyTypeError, '234', 5, 6)
        assert u(1) == 1
        with pytest.raises(ParseError) as ei:
            u(1.5)

        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, MyTypeError)
        assert err.args == ('234', 5, 6)

        u = validate(add.by(2), validity(is_type(int)), MyTypeError,
                     template('${V} is invalid', dict(V=keep())), 5, 6)
        assert u(1) == 1
        with pytest.raises(ParseError) as ei:
            u(1.5)

        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, MyTypeError)
        assert err.args == ('3.5 is invalid', 5, 6)
