import pytest
from hbutils.model import asitems, hasheq, visual, accessor

from argsloader.units import abs_, neg, to_type, inv, invert, pos, add, plus, sub, minus, not_, mul, matmul, \
    truediv, floordiv, mod, pow_, lshift, rshift, and_, or_, valid, is_type, band, bor, bxor


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

    def test_not_(self):
        u = not_()
        assert not u(True)
        assert u(False)

        u = not_(not_())
        assert u(True)
        assert not u(False)

        u = not_() >> not_()
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

        u = add(to_type(int))
        assert u(1.5) == 1
        assert u(-2.5) == -2

        u = add(to_type(int), 3, to_type(float))
        assert u(1.5) == 5.5
        assert u(-2.5) == -1.5

        with pytest.raises(TypeError):
            add()

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

        with pytest.raises(TypeError):
            sub(to_type(int))
        with pytest.raises(TypeError):
            sub(to_type(int), 2, 3)
        with pytest.raises(TypeError):
            sub()

    def test_mul(self):
        u = mul(to_type(int), to_type(float))
        assert u(1.5) == 1.5
        assert u(-2.5) == 5

        u = to_type(int) >> mul.by(2)
        assert u(1.5) == 2
        assert u(-2.5) == -4

        u = to_type(int) >> mul.from_(2)
        assert u(1.5) == 2
        assert u(-2.5) == -4

        u = mul(to_type(int))
        assert u(1.5) == 1
        assert u(-2.5) == -2

        u = mul(to_type(int), 3, to_type(float))
        assert u(1.5) == 4.5
        assert u(-2.5) == 15

    def test_matmul(self):
        @visual()
        @hasheq()
        @accessor(readonly=True)
        @asitems(['v'])
        class A:
            def __init__(self, v):
                self.__v = v

            def __matmul__(self, other):
                return A(self.v * other.v + 2)

        u = matmul(to_type(A), add.by(3) >> to_type(A))
        assert u(2) == A(12)
        assert u(5) == A(42)

        u = add.by(3) >> to_type(A) >> matmul.by(A(4))
        assert u(2) == A(22)
        assert u(5) == A(34)

        u = add.by(3) >> to_type(A) >> matmul.from_(A(4))
        assert u(2) == A(22)
        assert u(5) == A(34)

        u = matmul(to_type(A), A(4), add.by(3) >> to_type(A))
        assert u(2) == A(52)
        assert u(5) == A(178)

        u = matmul(to_type(A))
        assert u(2) == A(2)
        assert u(5) == A(5)

        with pytest.raises(TypeError):
            matmul()

    def test_truediv(self):
        u = truediv(to_type(float), to_type(int))
        assert u(1.5) == 1.5
        assert u(-2.5) == 1.25

        u = to_type(int) >> truediv.by(2)
        assert u(1.5) == 0.5
        assert u(-2.5) == -1

        u = to_type(int) >> truediv.from_(2)
        assert u(1.5) == 2
        assert u(-2.5) == -1

        with pytest.raises(TypeError):
            truediv(to_type(int))
        with pytest.raises(TypeError):
            truediv(to_type(int), 2, 3)
        with pytest.raises(TypeError):
            truediv()

    def test_floordiv(self):
        u = floordiv(to_type(float), to_type(int))
        assert u(1.5) == 1
        assert u(-2.5) == 1

        u = to_type(int) >> floordiv.by(2)
        assert u(1.5) == 0
        assert u(-2.5) == -1

        u = to_type(int) >> floordiv.from_(2)
        assert u(1.5) == 2
        assert u(-2.5) == -1

        with pytest.raises(TypeError):
            floordiv(to_type(int))
        with pytest.raises(TypeError):
            floordiv(to_type(int), 2, 3)
        with pytest.raises(TypeError):
            floordiv()

    def test_mod(self):
        u = mod(to_type(float), to_type(int))
        assert u(1.5) == 0.5
        assert u(-2.5) == -0.5

        u = to_type(int) >> mod.by(2)
        assert u(1.5) == 1
        assert u(-2.5) == 0

        u = to_type(int) >> mod.from_(2)
        assert u(1.5) == 0
        assert u(-2.5) == 0

        with pytest.raises(TypeError):
            mod(to_type(int))
        with pytest.raises(TypeError):
            mod(to_type(int), 2, 3)
        with pytest.raises(TypeError):
            mod()

    def test_pow_(self):
        u = pow_(to_type(float), to_type(int))
        assert u(1.5) == 1.5
        assert u(-2.5) == 0.16

        u = to_type(int) >> pow_.by(2)
        assert u(1.5) == 1
        assert u(-2.5) == 4

        u = to_type(int) >> pow_.from_(2)
        assert u(1.5) == 2
        assert u(-2.5) == 0.25

        with pytest.raises(TypeError):
            pow_(to_type(int))
        with pytest.raises(TypeError):
            pow_(to_type(int), 2, 3)
        with pytest.raises(TypeError):
            pow_()

    def test_lshift(self):
        u = lshift(add.by(7), sub.by(3))
        assert u(5) == 48
        assert u(6) == 104

        u = add.by(7) >> lshift.by(2)
        assert u(5) == 48
        assert u(6) == 52

        u = add.by(7) >> lshift.from_(2)
        assert u(5) == 8192
        assert u(6) == 16384

        with pytest.raises(TypeError):
            lshift(to_type(int))
        with pytest.raises(TypeError):
            lshift(to_type(int), 2, 3)
        with pytest.raises(TypeError):
            lshift()

    def test_rshift(self):
        u = rshift(add.by(7), sub.by(3))
        assert u(5) == 3
        assert u(6) == 1

        u = add.by(7) >> rshift.by(2)
        assert u(5) == 3
        assert u(6) == 3

        u = add.by(7) >> rshift.from_(0xffff)
        assert u(5) == 15
        assert u(6) == 7

        with pytest.raises(TypeError):
            rshift(to_type(int))
        with pytest.raises(TypeError):
            rshift(to_type(int), 2, 3)
        with pytest.raises(TypeError):
            rshift()

    def test_and_(self):
        class A:
            pass

        class B:
            pass

        class AB(A, B):
            pass

        u = and_(valid(is_type(A)), valid(is_type(B)))
        assert not u(A())
        assert not u(B())
        assert u(AB())

        u = and_(add.by(3), sub.by(4))
        assert u(5) == 1
        assert u(-3) == 0
        assert u(4) == 0

        u = add.by(3) >> and_.by(4)
        assert u(5) == 4
        assert u(-3) == 0
        assert u(4) == 4

        u = add.by(3) >> and_.from_(4)
        assert u(5) == 8
        assert u(-3) == 0
        assert u(4) == 7

        u = and_(add.by(3), sub.by(2), sub.by(4))
        assert u(5) == 1
        assert u(7) == 3
        assert u(-3) == 0
        assert u(4) == 0
        assert u(2) == 0

        u = and_(add.by(3))
        assert u(5) == 8
        assert u(7) == 10
        assert u(-3) == 0
        assert u(4) == 7
        assert u(2) == 5

        with pytest.raises(TypeError):
            and_()

    def test_or_(self):
        u = or_(valid(is_type(int)), valid(is_type(str)))
        assert u(1)
        assert not u(1.0)
        assert u('1')

        u = valid(is_type(int)) >> or_.by(valid(is_type(str)))
        assert u(1)
        assert not u(1.0)
        assert not u('1')

        u = valid(is_type(int)) >> or_.from_(valid(is_type(str)))
        assert u(1)
        assert not u(1.0)
        assert not u('1')

        u = or_(valid(is_type(int)), valid(is_type(str)), True)
        assert u(1)
        assert u(1.0)
        assert u('1')

        u = or_(valid(is_type(int)))
        assert u(1)
        assert not u(1.0)
        assert not u('1')

        with pytest.raises(TypeError):
            or_()

    def test_band(self):
        u = band(add.by(6), sub.by(3))
        assert u(51) == 48
        assert u(64) == 4

        u = add.by(6) >> band.by(0x55)
        assert u(51) == 17
        assert u(64) == 68

        u = add.by(6) >> band.from_(0x55)
        assert u(51) == 17
        assert u(64) == 68

        u = band(add.by(6), sub.by(3), 0x55)
        assert u(51) == 16
        assert u(64) == 4

        u = band(add.by(6))
        assert u(51) == 57
        assert u(64) == 70

        with pytest.raises(TypeError):
            band()

    def test_bor(self):
        u = bor(add.by(6), sub.by(3))
        assert u(51) == 57
        assert u(64) == 127

        u = add.by(6) >> bor.by(0x55)
        assert u(51) == 125
        assert u(64) == 87

        u = add.by(6) >> bor.from_(0x55)
        assert u(51) == 125
        assert u(64) == 87

        u = bor(add.by(6), sub.by(3), 0x55)
        assert u(51) == 125
        assert u(64) == 127

        u = bor(add.by(6))
        assert u(51) == 57
        assert u(64) == 70

        with pytest.raises(TypeError):
            bor()

    def test_bxor(self):
        u = bxor(add.by(6), sub.by(3))
        assert u(51) == 9
        assert u(64) == 123

        u = add.by(6) >> bxor.by(0x55)
        assert u(51) == 108
        assert u(64) == 19

        u = add.by(6) >> bxor.from_(0x55)
        assert u(51) == 108
        assert u(64) == 19

        u = bxor(add.by(6), sub.by(3), 0x55)
        assert u(51) == 92
        assert u(64) == 46

        u = bxor(add.by(6))
        assert u(51) == 57
        assert u(64) == 70

        with pytest.raises(TypeError):
            bxor()
