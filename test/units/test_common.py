import pytest

from argsloader.units import is_type, to_type


@pytest.mark.unittest
class TestUnitsCommon:
    def test_is_type(self):
        is_int = is_type(int)
        assert is_int(1) == 1
        assert is_int(2) == 2
        with pytest.raises(TypeError):
            _ = is_int(1.0)
        with pytest.raises(TypeError):
            _ = is_int('skldfjlsd')

    def test_to_type(self):
        to_int = to_type(int)
        assert to_int(1) == 1
        assert to_int(1.0) == 1
        assert to_int(1.314) == int(1.314)
        assert to_int('1357') == 1357
