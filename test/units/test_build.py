from textwrap import dedent
from typing import Mapping, Any

import pytest
from hbutils.collection import nested_map

from argsloader.base import ParseError, PValue, MultipleParseError
from argsloader.units import to_type, is_type, add, mul
from argsloader.units.build import TransformUnit, CalculateUnit, UnitBuilder, BaseUnit


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

    def test_unit_builder(self):
        class LinearFunctionBuilder(UnitBuilder):
            def __init__(self, k, b_):
                UnitBuilder.__init__(self)
                self.__k = k
                self.__b = b_

            def _build(self) -> BaseUnit:
                return is_type((float, int)) >> mul.by(self.__k) >> add.by(self.__b)

        b = LinearFunctionBuilder(2, 3)
        assert b(5) == 13
        assert b(0.5) == 4.0
        with pytest.raises(ParseError) as ei:
            b('dfsj')
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, TypeError)

        assert b.call(5) == 13
        assert b.call(0.5) == 4.0
        with pytest.raises(MultipleParseError) as ei:
            b.call('dfsj')
        err = ei.value
        assert len(err.items) == 1

        r = b.log(5)
        assert r.result.value == 13
        assert r.status.valid
        r = b.log(0.5)
        assert r.result.value == 4.0
        assert r.status.valid
        r = b.log('dfsj')
        assert r.status.processed
        assert not r.status.valid

        assert b.validity(5) is True
        assert b.validity(4.0) is True
        assert b.validity('sdlfjk') is False

        assert repr(b).strip() == dedent("""
<LinearFunctionBuilder, unit:
  <PipeUnit count: 3>
  ├── 0 --> <IsTypeUnit>
  │   └── type --> tuple(2)
  │       ├── 0 --> <class 'float'>
  │       └── 1 --> <class 'int'>
  ├── 1 --> <MulOpUnit>
  │   ├── v1 --> <KeepUnit>
  │   └── v2 --> 2
  └── 2 --> <AddOpUnit>
      ├── v1 --> <KeepUnit>
      └── v2 --> 3
>
        """).strip()

        u = b >> mul.by(-1)
        assert u(5) == -13
        assert u(0.5) == -4.0
        with pytest.raises(ParseError) as ei:
            u('dfsj')
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, TypeError)
