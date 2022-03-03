import pytest

from argsloader.base import ParseError
from argsloader.units import is_type, to_type


@pytest.mark.unittest
class TestUnitsOperator:
    def test_pipe(self):
        it = is_type((int, float, str)) >> to_type(float)
        assert len(it._units) == 2

        assert isinstance(it(1), float)
        assert it(1) == 1.0
        assert isinstance(it(1.5), float)
        assert it(1.5) == 1.5
        assert isinstance(it('-1.5'), float)
        assert it('-1.5') == -1.5

        with pytest.raises(ParseError) as ei:
            it(None)
        assert isinstance(ei.value, TypeError)

    def test_pip_chain(self):
        it = is_type((int, float, str)) >> to_type(float)
        it2 = it >> it >> it
        assert len(it._units) == 2
        assert len(it2._units) == 6

        assert isinstance(it2(1), float)
        assert it2(1) == 1.0
        assert isinstance(it2(1.5), float)
        assert it2(1.5) == 1.5
        assert isinstance(it2('-1.5'), float)
        assert it2('-1.5') == -1.5

        with pytest.raises(ParseError) as ei:
            it2(None)
        assert isinstance(ei.value, TypeError)
