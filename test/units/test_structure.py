from enum import Enum, unique
from textwrap import dedent

import pytest
from easydict import EasyDict

from argsloader.base import ParseError, MultipleParseError, PValue
from argsloader.units import getitem_, getattr_, struct, number, interval, mapping, check, add, in_, isin, contains, \
    mul, sub, to_type, is_type, cdict, cvalue, crequired, enum, cfree, positive, timespan


@pytest.mark.unittest
class TestUnitsStructure:
    def test_getitem_(self):
        u = getitem_('a')
        assert u({'a': 1, 'b': 2}) == 1
        assert u({'a': 10, 'b': 20}) == 10
        with pytest.raises(ParseError) as ei:
            u({'A': 1, 'b': 2})
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, KeyError)
        assert err.args == ("Item 'a' not found in value.",)

        u = getitem_(2)
        assert u([3, 5, 7]) == 7
        assert u([2, 3, 5, 7]) == 5
        with pytest.raises(ParseError) as ei:
            u([2, 3])
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, IndexError)
        assert err.args == ("Item 2 not found in value.",)

    def test_getitem_multiple(self):
        u = getitem_('a', 2)
        assert u({'a': [3, 5, 7, 9], 'b': 34}) == 7
        with pytest.raises(ParseError) as ei:
            u({'a': [3, 5], 'b': 34})
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, IndexError)

        with pytest.raises(ParseError) as ei:
            u({'aa': [3, 5, 7, 9], 'b': 34})
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, KeyError)

        u = getitem_()
        assert u({'a': [3, 5, 7, 9], 'b': 34}) == {'a': [3, 5, 7, 9], 'b': 34}
        assert u(1) == 1

    def test_getitem_position(self):
        u = getitem_('a')
        result = u.log({'a': 1, 'b': 2})
        assert result.result.position == ('a',)

        u = getitem_('a', offset=False)
        result = u.log({'a': 1, 'b': 2})
        assert result.result.position == ()

        u = getitem_(2)
        result = u.log([2, 3, 5])
        assert result.result.position == (2,)

        u = getitem_(2, offset=False)
        result = u.log([2, 3, 5])
        assert result.result.position == ()

    def test_getattr_(self):
        u = getattr_('a')
        assert u(EasyDict({'a': 1, 'b': 2})) == 1
        assert u(EasyDict({'a': 10, 'b': 20})) == 10
        with pytest.raises(ParseError) as ei:
            u(EasyDict({'A': 1, 'b': 2}))
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, AttributeError)
        assert err.args == ("'EasyDict' object has no attribute 'a'",)

    def test_struct(self):
        u = struct({
            'a': getitem_('a'),
            'b': getitem_('b'),
            'tuple': (getitem_('a'), getitem_('b')),
            'list': [getitem_('a'), getitem_('b')],
            'easydict': EasyDict({
                'a': getitem_('a'),
                'b': getitem_('b'),
            })
        })

        result = u({'a': 1, 'b': 2})
        assert result == {
            'a': 1, 'b': 2,
            'tuple': (1, 2),
            'list': [1, 2],
            'easydict': EasyDict({'a': 1, 'b': 2}),
        }
        assert isinstance(result['easydict'], EasyDict)

        assert repr(u).strip() == dedent("""
            <StructUnit>
            └── struct --> dict(a, b, tuple, list, easydict)
                ├── a --> <GetItemUnit offset: True>
                │   └── item --> 'a'
                ├── b --> <GetItemUnit offset: True>
                │   └── item --> 'b'
                ├── tuple --> tuple(2)
                │   ├── 0 --> <GetItemUnit offset: True>
                │   │   └── item --> 'a'
                │   └── 1 --> <GetItemUnit offset: True>
                │       └── item --> 'b'
                ├── list --> list(2)
                │   ├── 0 --> <GetItemUnit offset: True>
                │   │   └── item --> 'a'
                │   └── 1 --> <GetItemUnit offset: True>
                │       └── item --> 'b'
                └── easydict --> EasyDict(a, b)
                    ├── a --> <GetItemUnit offset: True>
                    │   └── item --> 'a'
                    └── b --> <GetItemUnit offset: True>
                        └── item --> 'b'
        """).strip()

        u = struct(getitem_('a'))
        assert u({'a': 1, 'b': 2}) == 1

    def test_struct_error(self):
        u = struct({
            'a': (getitem_('a') | getitem_('first')) >> number() >> interval.lR(3, 10),
            'b': (getitem_('b') | getitem_('second')) >> number() >> interval.R(5),
        })
        assert u({'a': 4.5, 'b': 5}) == {'a': 4.5, 'b': 5}

        with pytest.raises(ParseError) as ei:
            u({'first': 11, 'b': 5})
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ('Value not in interval - (3, 10] expected but 11 found.',)

        with pytest.raises(MultipleParseError) as ei:
            u.call({'first': 11, 'b': 6})
        err = ei.value
        assert isinstance(err, MultipleParseError)
        assert len(err.items) == 2
        assert err.items[0][0].position == ('first',)
        assert err.items[0][1].message == 'Value not in interval - (3, 10] expected but 11 found.'
        assert err.items[1][0].position == ('b',)
        assert err.items[1][1].message == 'Value not in interval - [-inf, 5] expected but 6 found.'

    # noinspection DuplicatedCode
    def test_mapping_simple(self):
        u = mapping(to_type(int))
        assert u([1, 2.3, '15']) == [1, 2, 15]
        assert u((1, 2.3, '15')) == (1, 2, 15)

        u = mapping(is_type(int) >> add.by(2) >> interval.LR(1, 10))
        assert u([1, 3, 7]) == [3, 5, 9]
        assert u((1, 3, 7)) == (3, 5, 9)

        with pytest.raises(ParseError) as ei:
            u([1.0, 3, 9])
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, TypeError)
        assert err.args == ('Value type not match - int expected but float found.',)

        with pytest.raises(ParseError) as ei:
            u([1, 3, 9])
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ('Value not in interval - [1, 10] expected but 11 found.',)

        with pytest.raises(MultipleParseError) as ei:
            u.call([1.0, 3, 9])
        err = ei.value
        assert err.items[0][0] == PValue(1.0, (0,))
        assert err.items[0][1].args == ('Value type not match - int expected but float found.',)
        assert err.items[1][0] == PValue(11, (2,))
        assert err.items[1][1].args == ('Value not in interval - [1, 10] expected but 11 found.',)

    # noinspection DuplicatedCode
    def test_mapping_without_offset(self):
        u = mapping(is_type(int) >> add.by(2) >> interval.LR(1, 10), offset=False)
        assert u([1, 3, 7]) == [3, 5, 9]
        assert u((1, 3, 7)) == (3, 5, 9)

        with pytest.raises(ParseError) as ei:
            u([1.0, 3, 9])
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, TypeError)
        assert err.args == ('Value type not match - int expected but float found.',)

        with pytest.raises(ParseError) as ei:
            u([1, 3, 9])
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ('Value not in interval - [1, 10] expected but 11 found.',)

        with pytest.raises(MultipleParseError) as ei:
            u.call([1.0, 3, 9])
        err = ei.value
        assert err.items[0][0] == PValue(1.0, ())
        assert err.items[0][1].args == ('Value type not match - int expected but float found.',)
        assert err.items[1][0] == PValue(11, ())
        assert err.items[1][1].args == ('Value not in interval - [1, 10] expected but 11 found.',)

    def test_mapping(self):
        u = mapping(struct({
            'a': (getitem_('a') | getitem_('first')) >> number(),
            'b': (getitem_('b') | getitem_('second')) >> number(),
        }) >> check(
            (getitem_('a') >> interval.lR(3, 10)) &
            (getitem_('b') >> interval.R(5).l(150)) &
            (add(getitem_('a'), getitem_('b')) >> interval.LR(0, 12))
        ))

        assert repr(u).strip() == dedent("""
            <MappingUnit>
            └── func --> <PipeUnit count: 2>
                ├── 0 --> <StructUnit>
                │   └── struct --> dict(a, b)
                │       ├── a --> <PipeUnit count: 2>
                │       │   ├── 0 --> <OrUnit count: 2>
                │       │   │   ├── 0 --> <GetItemUnit offset: True>
                │       │   │   │   └── item --> 'a'
                │       │   │   └── 1 --> <GetItemUnit offset: True>
                │       │   │       └── item --> 'first'
                │       │   └── 1 --> <NumberUnit>
                │       └── b --> <PipeUnit count: 2>
                │           ├── 0 --> <OrUnit count: 2>
                │           │   ├── 0 --> <GetItemUnit offset: True>
                │           │   │   └── item --> 'b'
                │           │   └── 1 --> <GetItemUnit offset: True>
                │           │       └── item --> 'second'
                │           └── 1 --> <NumberUnit>
                └── 1 --> <CheckUnit>
                    └── unit --> <AndUnit count: 3>
                        ├── 0 --> <PipeUnit count: 2>
                        │   ├── 0 --> <GetItemUnit offset: True>
                        │   │   └── item --> 'a'
                        │   └── 1 --> <IntervalUnit>
                        │       └── condition --> <ValidityUnit>
                        │           └── unit --> <AndUnit count: 2>
                        │               ├── 0 --> <GtCheckUnit>
                        │               │   ├── v1 --> <KeepUnit>
                        │               │   └── v2 --> 3
                        │               └── 1 --> <LeCheckUnit>
                        │                   ├── v1 --> <KeepUnit>
                        │                   └── v2 --> 10
                        ├── 1 --> <PipeUnit count: 2>
                        │   ├── 0 --> <GetItemUnit offset: True>
                        │   │   └── item --> 'b'
                        │   └── 1 --> <IntervalUnit>
                        │       └── condition --> <ValidityUnit>
                        │           └── unit --> <OrUnit count: 2>
                        │               ├── 0 --> <AndUnit count: 2>
                        │               │   ├── 0 --> <GeCheckUnit>
                        │               │   │   ├── v1 --> <KeepUnit>
                        │               │   │   └── v2 --> -inf
                        │               │   └── 1 --> <LeCheckUnit>
                        │               │       ├── v1 --> <KeepUnit>
                        │               │       └── v2 --> 5
                        │               └── 1 --> <AndUnit count: 2>
                        │                   ├── 0 --> <GtCheckUnit>
                        │                   │   ├── v1 --> <KeepUnit>
                        │                   │   └── v2 --> 150
                        │                   └── 1 --> <LeCheckUnit>
                        │                       ├── v1 --> <KeepUnit>
                        │                       └── v2 --> inf
                        └── 2 --> <PipeUnit count: 2>
                            ├── 0 --> <AddOpUnit>
                            │   ├── v1 --> <GetItemUnit offset: True>
                            │   │   └── item --> 'a'
                            │   └── v2 --> <GetItemUnit offset: True>
                            │       └── item --> 'b'
                            └── 1 --> <IntervalUnit>
                                └── condition --> <ValidityUnit>
                                    └── unit --> <AndUnit count: 2>
                                        ├── 0 --> <GeCheckUnit>
                                        │   ├── v1 --> <KeepUnit>
                                        │   └── v2 --> 0
                                        └── 1 --> <LeCheckUnit>
                                            ├── v1 --> <KeepUnit>
                                            └── v2 --> 12
        """).strip()

        assert u([
            {'a': 4.0, 'second': '0x5'},
            {'first': '0b101', 'b': 3.5},
        ]) == [
                   {'a': 4.0, 'b': 5},
                   {'a': 5, 'b': 3.5},
               ]

        with pytest.raises(MultipleParseError) as ei:
            u.call([
                {'a': 1, 'second': '0x64'},
                {'first': '0b101', 'b': 5.5},
            ])
        err = ei.value
        assert isinstance(err, MultipleParseError)
        assert len(err.items) == 4
        assert set(map(lambda x: x[0].position, err.items)) == \
               {(0, 'a'), (0, 'b'), (0,), (1, 'b')}

    def test_in_(self):
        u = in_(add.by(2), [3, 4, 5])
        assert u(1) == 1
        assert u(2) == 2
        with pytest.raises(ParseError) as ei:
            u(4)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, KeyError)
        assert err.args == ('Collection should contain instance, but 6 is not included in [3, 4, 5] actually.',)

        u = add.by(2) >> isin([3, 4, 5])
        assert u(1) == 3
        assert u(2) == 4
        with pytest.raises(ParseError) as ei:
            u(4)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, KeyError)
        assert err.args == ('Collection should contain instance, but 6 is not included in [3, 4, 5] actually.',)

        u = struct([add.by(2), mul.by(2), sub.by(2)]) >> contains(4)
        assert u(2) == [4, 4, 0]
        assert u(6) == [8, 12, 4]
        with pytest.raises(ParseError) as ei:
            u(7)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, KeyError)
        assert err.args == ('Collection should contain instance, but 4 is not included in [9, 14, 5] actually.',)

        u = in_(add.by(2), 1)
        with pytest.raises(ParseError) as ei:
            u(7)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, TypeError)

    def test_cdict(self):
        u = cdict({
            'a': 1,
            'b': 2,
        })
        assert u({}) == {'a': 1, 'b': 2}
        assert u({'a': 10}) == {'a': 10, 'b': 2}
        assert u({'a': 10, 'c': -1}) == {'a': 10, 'b': 2}

        u = cdict(EasyDict({
            'a': 1,
            'b': 2,
        }))
        assert u({}) == {'a': 1, 'b': 2}
        assert isinstance(u({}), EasyDict)
        assert u({'a': 10}) == {'a': 10, 'b': 2}
        assert isinstance(u({'a': 10}), EasyDict)
        assert u({'a': 10, 'c': -1}) == {'a': 10, 'b': 2}
        assert isinstance(u({'a': 10, 'c': -1}), EasyDict)

    def test_cdict_with_cvalue(self):
        u = cdict({
            'a': 1,
            'b': cvalue(2, is_type(int)),
            'c': {
                'x': cvalue(3, is_type(int) >> add.by(2)),
                'y': cvalue(4, is_type(int) & interval.LR(0, 10)),
            }
        })
        assert u({}) == {'a': 1, 'b': 2, 'c': {'x': 5, 'y': 4}}
        assert u({'a': 5, 'b': 4, 'c': {'x': 18}}) == {'a': 5, 'b': 4, 'c': {'x': 20, 'y': 4}}

        with pytest.raises(ParseError) as ei:
            u({'b': 2.0})
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, TypeError)

        with pytest.raises(ParseError) as ei:
            u({'c': {'x': 3.0}})
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, TypeError)

        with pytest.raises(ParseError) as ei:
            u({'c': {'y': 4.0}})
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, TypeError)

        with pytest.raises(ParseError) as ei:
            u({'c': {'y': 12}})
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)

        with pytest.raises(MultipleParseError) as ei:
            u.call({
                'a': 5,
                'b': 4.0,
                'c': {
                    'x': 8.0,
                    'y': 12.0,
                }
            })
        err = ei.value
        assert len(err.items) == 4

    def test_cdict_with_crequired(self):
        u = cdict({
            'a': crequired(),
            'b': cvalue(2, is_type(int)),
            'c': {
                'x': cvalue(crequired(), is_type(int) >> add.by(2)),
                'y': cvalue(4, is_type(int) & interval.LR(0, 10)),
            }
        })
        with pytest.raises(ParseError) as ei:
            u({})
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, KeyError)

        with pytest.raises(ParseError) as ei:
            u({'a': 5})
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, KeyError)

        with pytest.raises(ParseError) as ei:
            u({'c': {'x': 5}})
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, KeyError)

        assert u({'a': 4, 'c': {'x': 5}}) == {'a': 4, 'b': 2, 'c': {'x': 7, 'y': 4}}

        with pytest.raises(MultipleParseError) as ei:
            u.call({'b': 2.0, 'c': {'y': 12.0}})
        err = ei.value
        assert len(err.items) == 5

    # noinspection DuplicatedCode
    def test_cdict_nested(self):
        ux = cdict({
            'x': cvalue(3, is_type(int) >> add.by(2)),
            'y': cvalue(4, is_type(int) & interval.LR(0, 10)),
        })
        u = cdict({
            'a': 1,
            'b': cvalue(2, is_type(int)),
            'c': ux,
        })
        assert u({}) == {'a': 1, 'b': 2, 'c': {'x': 5, 'y': 4}}
        assert u({'a': 5, 'b': 4, 'c': {'x': 18}}) == {'a': 5, 'b': 4, 'c': {'x': 20, 'y': 4}}

        with pytest.raises(ParseError) as ei:
            u({'b': 2.0})
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, TypeError)

        with pytest.raises(ParseError) as ei:
            u({'c': {'x': 3.0}})
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, TypeError)

    def test_cdict_with_cfree(self):
        @unique
        class MyType(Enum):
            SAMPLE = 1
            STEP = 2
            EPISODE = 3

        u = cdict({
            'n': {
                'type': cfree(
                    (
                            (getitem_('n_sample') & 'sample') |
                            (getitem_('n_step') & 'step') |
                            (getitem_('n_episode') & 'episode') |
                            'sample'
                    ) >> enum(MyType),
                ),
                'number': cfree(
                    (
                            getitem_('n_sample') |
                            getitem_('n_step') |
                            getitem_('n_episode') |
                            12
                    ) >> number() >> positive()
                )
            },
            'time': cvalue(12, timespan()),
        })
        assert u({'n': {'n_episode': 77}, 'time': '8min'}) == {
            'n': {
                'type': MyType.EPISODE,
                'number': 77,
            },
            'time': 480.0,
        }
        assert u({}) == {
            'n': {
                'type': MyType.SAMPLE,
                'number': 12,
            },
            'time': 12,
        }
        assert u({'time': '1day'}) == {
            'n': {
                'type': MyType.SAMPLE,
                'number': 12,
            },
            'time': 86400.0,
        }
