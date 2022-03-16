from textwrap import dedent

import pytest

from argsloader.base import PValue, ParseResult, ParseError
from argsloader.units import raw
from argsloader.units.base import BaseUnit, UnitProcessProxy, UncompletedUnit


@pytest.mark.unittest
class TestUnitsBase:
    def test_uncompleted_unit(self):
        class _F:
            def __init__(self, s):
                self._s = s

            def __repr__(self):
                return str(self._s)

        class UUnit(UncompletedUnit):
            def _fail(self):
                raise SyntaxError('this unit is uncompleted.')

            def _rinfo(self):
                return (
                    [('x', 1)],
                    [
                        ('y', {'a': _F('1\n2\n3'), 'b': (4, 5, 6)}),
                        ('z', [_F('ab\ncd\nefg'), 234]),
                    ]
                )

        with pytest.raises(SyntaxError):
            UUnit()(1)
        with pytest.raises(SyntaxError):
            UUnit().call(1)
        with pytest.raises(SyntaxError):
            UUnit().log(1)
        with pytest.raises(SyntaxError):
            _ = UUnit().validity
        with pytest.raises(SyntaxError):
            # noinspection PyUnresolvedReferences
            _ = UUnit() >> raw(2)

        assert repr(UUnit()).strip() == dedent("""
            <(X)UUnit x: 1>
            ├── y --> dict(a, b)
            │   ├── a --> 1
            │   │         2
            │   │         3
            │   └── b --> tuple(3)
            │       ├── 0 --> 4
            │       ├── 1 --> 5
            │       └── 2 --> 6
            └── z --> list(2)
                ├── 0 --> ab
                │         cd
                │         efg
                └── 1 --> 234
        """).strip()

    # noinspection DuplicatedCode
    def test_base_unit(self):
        class MyUnit(BaseUnit):
            def __init__(self, x):
                self._x = x

            def _easy_process(self, v: PValue, proxy: UnitProcessProxy) -> ParseResult:
                if v.value + self._x < 0:
                    return proxy.error(ValueError('verr', v.value), {'x': self._x})
                else:
                    return proxy.success(v.val(v.value + self._x), {'x': self._x})

            def _rinfo(self):
                return [('x', self._x)], []

        u = MyUnit(2)
        assert u(3) == 5
        assert u.call(3) == 5
        ures = u.log(3)
        assert ures.input == PValue(3, ())
        assert ures.result == PValue(5, ())
        assert ures['x'] == 2

        with pytest.raises(ParseError) as ei:
            u(-10)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ('verr', -10)

        u = MyUnit(2).validity
        assert u(3) is True
        assert u.call(3) is True
        assert u(-10) is False
        assert u.call(-10) is False

        u = MyUnit(-2) >> MyUnit(-5)
        assert u(10) == 3
        assert u(7) == 0
        with pytest.raises(ParseError) as ei:
            u(5)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ('verr', 3)

        u = 8 >> MyUnit(-5)
        assert u(10) == 3
        assert u(7) == 3
        assert u(-10) == 3

        u = MyUnit(2) & MyUnit(5)
        assert u(3) == 8
        assert u(-2) == 3
        with pytest.raises(ParseError) as ei:
            u(-10)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ('verr', -10)

        u = 2 & MyUnit(5)
        assert u(3) == 8
        assert u(-2) == 3
        with pytest.raises(ParseError) as ei:
            u(-10)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ('verr', -10)

        u = MyUnit(2) | MyUnit(5)
        assert u(3) == 5
        assert u(-3) == 2
        with pytest.raises(ParseError) as ei:
            u(-10)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ('verr', -10)

        u = 2 | MyUnit(2)
        assert u(3) == 2
        assert u(-3) == 2
        assert u(-10) == 2

    def test_raw(self):
        u = raw(1)
        assert u(1) == 1
        assert u(2.0) == 1
        assert u('sdklfj') == 1
        assert u(pytest) == 1

        assert repr(u).strip() == dedent("""
            <ValueUnit>
            └── value --> 1
        """).strip()

        class XUnit(BaseUnit):
            def __init__(self, *vs):
                self._vs = vs

            def _easy_process(self, v: PValue, proxy: UnitProcessProxy) -> ParseResult:
                return proxy.success(v, )

            def _rinfo(self):
                return [], [(i, v) for i, v in enumerate(self._vs)]

        assert repr(XUnit(raw(1), raw([4, 5]), raw({'x': 3, 'y': 7}))).strip() == dedent("""
            <XUnit>
            ├── 0 --> 1
            ├── 1 --> [4, 5]
            └── 2 --> {'x': 3, 'y': 7}
        """).strip()
