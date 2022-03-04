import pytest

from argsloader.base import ParseError
from argsloader.units import keep, check, is_type, to_type, valid


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

    def test_valid(self):
        u = valid(is_type(int) | is_type(str))
        assert u(1)
        assert not u(1.0)
        assert u('sdkjf')
