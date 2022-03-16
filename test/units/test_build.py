from textwrap import dedent
from typing import Mapping, Any

import pytest
from hbutils.collection import nested_map

from argsloader.base import ParseError, PValue
from argsloader.units import to_type, is_type
from argsloader.units.build import TransformUnit, CalculateUnit


@pytest.mark.unittest
class TestUnitsBuild:
    # noinspection DuplicatedCode
    def test_transform_unit(self):
        class MyUnit(TransformUnit):
            __names__ = ('x1', 'x2')
            __errors__ = (ValueError,)

            def __init__(self, *xx):
                TransformUnit.__init__(self, *xx)

            def _transform(self, v: PValue, pres: Mapping[str, Any]) -> PValue:
                v1, v2 = nested_map(lambda x: x.value, pres['x1']), pres['x2'].value
                if v.value >= 0:
                    return v.val(v.value + sum(v1) + v2)
                else:
                    raise ValueError('verr', v1, v2)

        u = MyUnit([to_type(int), 2, is_type(int), to_type(int)], 2)
        assert u(2) == 12
        assert repr(u).strip() == dedent("""
            <MyUnit>
            ├── x1 --> list(4)
            │   ├── 0 --> <ToTypeUnit>
            │   │   └── type --> <class 'int'>
            │   ├── 1 --> 2
            │   ├── 2 --> <IsTypeUnit>
            │   │   └── type --> <class 'int'>
            │   └── 3 --> <ToTypeUnit>
            │       └── type --> <class 'int'>
            └── x2 --> 2
        """).strip()

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

        with pytest.raises(TypeError):
            MyUnit(2, 3, 4)
        with pytest.raises(TypeError):
            MyUnit(2)

    # noinspection DuplicatedCode
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
