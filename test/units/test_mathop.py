import pytest
from hbutils.model import asitems, hasheq, visual, accessor

from argsloader.units import abs_, neg, to_type, inv, invert, pos, add, plus, sub, minus, lnot


@pytest.mark.unittest
class TestUtilsMathop:
    def test_abs_(self):
        u = abs_()
        assert u(1) == 1
        assert u(1.5) == 1.5
        assert u(-2.5) == 2.5

        u = to_type(int) >> abs_()
        assert u(1) == 1
        assert u(1.5) == 1
        assert u(-2.5) == 2

        u = abs_(to_type(int))
        assert u(1) == 1
        assert u(1.5) == 1
        assert u(-2.5) == 2

    def test_neg(self):
        u = neg()
        assert u(1) == -1
        assert u(1.5) == -1.5
        assert u(-2.5) == 2.5

        u = to_type(int) >> neg()
        assert u(1) == -1
        assert u(1.5) == -1
        assert u(-2.5) == 2

        u = neg(to_type(int))
        assert u(1) == -1
        assert u(1.5) == -1
        assert u(-2.5) == 2

    def test_inv(self):
        assert inv is invert

        u = inv()
        assert u(13) == ~13
        assert u(0) == ~0
        assert u(-384) == ~-384

        u = to_type(int) >> inv()
        assert u(13.043) == ~13
        assert u(0.230) == ~0
        assert u(-384.2332) == ~-384

        u = inv(to_type(int))
        assert u(13.043) == ~13
        assert u(0.230) == ~0
        assert u(-384.2332) == ~-384

    def test_pos(self):
        @visual()
        @hasheq()
        @accessor(readonly=True)
        @asitems(['v'])
        class _Pos:
            def __init__(self, v):
                self.__v = v

            def __pos__(self):
                return _Pos(-self.v)

        u = pos()
        assert u(1) == 1
        assert u(-1.5) == -1.5
        assert u(_Pos(2.5)) == _Pos(-2.5)
        assert u(_Pos(-4.5)) == _Pos(4.5)

        u = to_type(_Pos) >> pos()
        assert u(2.5) == _Pos(-2.5)
        assert u(-4.5) == _Pos(4.5)

        u = pos(to_type(_Pos))
        assert u(2.5) == _Pos(-2.5)
        assert u(-4.5) == _Pos(4.5)

    def test_lnot(self):
        u = lnot()
        assert not u(True)
        assert u(False)

        u = lnot(lnot())
        assert u(True)
        assert not u(False)

        u = lnot() >> lnot()
        assert u(True)
        assert not u(False)

    def test_add(self):
        assert plus is add

        u = add(to_type(int), to_type(float))
        assert u(1.5) == 2.5
        assert u(-2.5) == -4.5

        u = to_type(float) >> add.by(2)
        assert u(1.5) == 3.5
        assert u(-2.5) == -0.5

        u = to_type(float) >> add.from_(2)
        assert u(1.5) == 3.5
        assert u(-2.5) == -0.5

    def test_sub(self):
        assert minus is sub

        u = sub(to_type(int), to_type(float))
        assert u(1.5) == -0.5
        assert u(-2.5) == 0.5

        u = to_type(int) >> sub.by(2)
        assert u(1.5) == -1
        assert u(-2.5) == -4

        u = to_type(int) >> sub.from_(2)
        assert u(1.5) == 1
        assert u(-2.5) == 4
