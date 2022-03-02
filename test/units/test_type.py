import pytest

from argsloader.base import MultipleParseError, ParseError
from argsloader.units import is_type


@pytest.mark.unittest
class TestUnitsType:
    def test_is_type(self):
        it = is_type(int)
        assert it(1) == 1
        assert it(2) == 2

        with pytest.raises(MultipleParseError) as ei:
            _ = it('skldfj')

        err = ei.value
        eitems = err.items
        assert len(eitems) == 1
        assert eitems[0][0].position == ()
        assert isinstance(eitems[0][1], TypeError)
        assert isinstance(eitems[0][1], ParseError)
