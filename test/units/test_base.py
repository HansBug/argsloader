from typing import Mapping, Any

import pytest

from argsloader.base import PValue, ParseResult, ParseError
from argsloader.units import raw, to_type, is_type
from argsloader.units.base import BaseUnit, UnitProcessProxy, UncompletedUnit, TransformUnit, CalculateUnit


@pytest.mark.unittest
class TestUnitsBase:
    def test_uncompleted_unit(self):
        class UUnit(UncompletedUnit):
            def _fail(self):
                raise SyntaxError('this unit is uncompleted.')

            def _rinfo(self):
                return [], []

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

    def test_transform_unit(self):
        class MyUnit(TransformUnit):
            __names__ = ('x1', 'x2')
            __errors__ = (ValueError,)

            def __init__(self, x1, x2):
                TransformUnit.__init__(self, x1, x2)

            def _transform(self, v: PValue, pres: Mapping[str, Any]) -> PValue:
                if v.value >= 0:
                    return v.val(v.value + sum(pres['x1']) + pres['x2'])
                else:
                    raise ValueError('verr', pres['x1'], pres['x2'])

        u = MyUnit([to_type(int), 2, is_type(int), to_type(int)], 2)
        assert u(2) == 12

        with pytest.raises(ParseError) as ei:
            u(3.5)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, TypeError)
        assert err.args == ('Value type not match - int expected but float found.',)

        with pytest.raises(ParseError) as ei:
            u(-3)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ('verr', [-3, 2, -3, -3], 2)

    def test_calculate_unit(self):
        class MyUnit(CalculateUnit):
            __names__ = ('x1', 'x2')
            __errors__ = (ValueError,)

            def __init__(self, x1, x2):
                TransformUnit.__init__(self, x1, x2)

            def _calculate(self, v, pres: Mapping[str, Any]) -> object:
                if v >= 0:
                    return v + sum(pres['x1']) + pres['x2']
                else:
                    raise ValueError('verr', pres['x1'], pres['x2'])

        u = MyUnit([to_type(int), 2, is_type(int), to_type(int)], 2)
        assert u(2) == 12

        with pytest.raises(ParseError) as ei:
            u(3.5)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, TypeError)
        assert err.args == ('Value type not match - int expected but float found.',)

        with pytest.raises(ParseError) as ei:
            u(-3)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ('verr', [-3, 2, -3, -3], 2)
