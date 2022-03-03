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

    def test_pipe_extra(self):
        it = is_type(int) >> 2
        assert it(3) == 2
        with pytest.raises(TypeError):
            _ = it(4.39284)

        it = 2 >> is_type(int)
        assert it(3) == 2
        assert it(4.39284) == 2

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

    def test_and_extra(self):
        it = is_type(int) & 2
        assert it(3) == 2
        with pytest.raises(TypeError):
            _ = it(3.94835)

        it = 2 & is_type(int)
        assert it(3) == 3
        with pytest.raises(TypeError):
            _ = it(3.94835)

    def test_or_(self):
        it = is_type(int) | is_type(float)
        assert it(1) == 1
        assert it(1.5) == 1.5
        with pytest.raises(ParseError) as ei:
            _ = it('-1.5')

        err = ei.value
        assert isinstance(err, TypeError)
        assert isinstance(err, ParseError)

    def test_or_chain(self):
        it = is_type(int) | is_type(float)
        assert len(it._units) == 2

        assert len((it | it | it)._units) == 6
        assert len((it | (it & it) | it)._units) == 5
        assert len((it | (it >> it) | it)._units) == 5
        assert len((it | (it | it) | it)._units) == 8

    def test_or_extra(self):
        it = is_type(int) | 2
        assert it(3) == 3
        assert it(1) == 1
        assert it(1.2) == 2

        it = 2 | is_type(int)
        assert it(3) == 2
        assert it(1) == 2
        assert it(1.2) == 2
        assert it(None) == 2

        it = (is_type(int) >> 'this is int') | (is_type(float) >> 'this is float') | 'fxxk'
        assert it(1) == 'this is int'
        assert it(1.5) == 'this is float'
        assert it('sdklfj') == 'fxxk'
