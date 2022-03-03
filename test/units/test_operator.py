import pytest

from argsloader.base import ParseError
from argsloader.units import is_type, to_type


class A:
    pass


class B:
    pass


class AB(A, B):
    pass


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

    def test_pipe_chain(self):
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

    def test_and_(self):
        it = is_type(A) & is_type(B)

        o1 = AB()
        assert it(o1) is o1

        o2 = A()
        with pytest.raises(ParseError) as ei:
            _ = it(o2)

        err = ei.value
        assert isinstance(err, TypeError)
        assert isinstance(err, ParseError)

        o3 = B()
        with pytest.raises(ParseError) as ei:
            _ = it(o3)

        err = ei.value
        assert isinstance(err, TypeError)
        assert isinstance(err, ParseError)

    def test_and_chain(self):
        it = is_type(A) & is_type(B)
        assert len(it._units) == 2

        assert len((it & (it >> it) & it)._units) == 5
