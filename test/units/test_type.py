import pytest

from argsloader.base import MultipleParseError, ParseError
from argsloader.units import is_type, to_type


@pytest.mark.unittest
class TestUnitsType:
    def test_is_type(self):
        it = is_type(int)
        assert it(1) == 1
        assert it(2) == 2

        with pytest.raises(MultipleParseError) as ei:
            _ = it(2.0)

        err = ei.value
        eitems = err.items
        assert len(eitems) == 1
        assert eitems[0][0].value == 2.0
        assert eitems[0][0].position == ()
        assert isinstance(eitems[0][1], TypeError)
        assert isinstance(eitems[0][1], ParseError)

    def test_is_type_with_tuple(self):
        it = is_type((int, float))
        assert it(1) == 1
        assert it(2) == 2
        assert it(2.0) == 2.0

        with pytest.raises(MultipleParseError) as ei:
            _ = it('2.0')

        err = ei.value
        eitems = err.items
        assert len(eitems) == 1
        assert eitems[0][0].value == '2.0'
        assert eitems[0][0].position == ()
        assert isinstance(eitems[0][1], TypeError)
        assert isinstance(eitems[0][1], ParseError)

    def test_to_type(self):
        ot = to_type(int)
        assert ot(1) == 1
        assert ot('1') == 1
        assert ot(1.5) == int(1.5)

        with pytest.raises(MultipleParseError) as ei:
            _ = ot('1.5')

        err = ei.value
        eitems = err.items
        assert len(eitems) == 1
        assert eitems[0][0].value == '1.5'
        assert eitems[0][0].position == ()
        assert isinstance(eitems[0][1], ValueError)
        assert isinstance(eitems[0][1], ParseError)
