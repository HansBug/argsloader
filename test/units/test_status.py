import pytest

from argsloader.units import child, parent


@pytest.mark.unittest
class TestUnitsStatus:
    def test_child(self):
        u = child('a', 'b')
        assert u(1) == 1
        assert u.log(1).result.position == ('a', 'b')

    def test_parent(self):
        u = child('a', 'b') >> parent()
        assert u(1) == 1
        assert u.log(1).result.position == ('a',)

        u = child('a', 'b') >> parent(2)
        assert u(1) == 1
        assert u.log(1).result.position == ()
