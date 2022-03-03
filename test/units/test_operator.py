import pytest

from argsloader.units import is_type, to_type


@pytest.mark.unittest
class TestUnitsOperator:
    def test_pipe(self):
        it = is_type((int, float, str)) >> to_type(float)
        assert isinstance(it(1), float)
        assert it(1) == 1.0
        assert isinstance(it(1.5), float)
        assert it(1.5) == 1.5
        assert isinstance(it('-1.5'), float)
        assert it('-1.5') == -1.5
