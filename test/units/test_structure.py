from textwrap import dedent

import pytest
from easydict import EasyDict

from argsloader.base import ParseError, MultipleParseError
from argsloader.units import getitem_, getattr_, struct, number, interval


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
        assert err.args == ("Item 'a' not found.",)

        u = getitem_(2)
        assert u([3, 5, 7]) == 7
        assert u([2, 3, 5, 7]) == 5
        with pytest.raises(ParseError) as ei:
            u([2, 3])
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, IndexError)
        assert err.args == ("Item 2 not found.",)

    def test_getitem_position(self):
        u = getitem_('a')
        result = u.log({'a': 1, 'b': 2})
        assert result.result.position == ('a',)

        u = getitem_('a', no_follow=True)
        result = u.log({'a': 1, 'b': 2})
        assert result.result.position == ()

        u = getitem_(2)
        result = u.log([2, 3, 5])
        assert result.result.position == (2,)

        u = getitem_(2, no_follow=True)
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
                ├── a --> <PipeUnit count: 2>
                │   ├── 0 --> <GetItemUnit>
                │   │   └── item --> 'a'
                │   └── 1 --> <ChildPositionUnit>
                │       └── children --> tuple(1)
                │           └── 0 --> 'a'
                ├── b --> <PipeUnit count: 2>
                │   ├── 0 --> <GetItemUnit>
                │   │   └── item --> 'b'
                │   └── 1 --> <ChildPositionUnit>
                │       └── children --> tuple(1)
                │           └── 0 --> 'b'
                ├── tuple --> tuple(2)
                │   ├── 0 --> <PipeUnit count: 2>
                │   │   ├── 0 --> <GetItemUnit>
                │   │   │   └── item --> 'a'
                │   │   └── 1 --> <ChildPositionUnit>
                │   │       └── children --> tuple(1)
                │   │           └── 0 --> 'a'
                │   └── 1 --> <PipeUnit count: 2>
                │       ├── 0 --> <GetItemUnit>
                │       │   └── item --> 'b'
                │       └── 1 --> <ChildPositionUnit>
                │           └── children --> tuple(1)
                │               └── 0 --> 'b'
                ├── list --> list(2)
                │   ├── 0 --> <PipeUnit count: 2>
                │   │   ├── 0 --> <GetItemUnit>
                │   │   │   └── item --> 'a'
                │   │   └── 1 --> <ChildPositionUnit>
                │   │       └── children --> tuple(1)
                │   │           └── 0 --> 'a'
                │   └── 1 --> <PipeUnit count: 2>
                │       ├── 0 --> <GetItemUnit>
                │       │   └── item --> 'b'
                │       └── 1 --> <ChildPositionUnit>
                │           └── children --> tuple(1)
                │               └── 0 --> 'b'
                └── easydict --> EasyDict(a, b)
                    ├── a --> <PipeUnit count: 2>
                    │   ├── 0 --> <GetItemUnit>
                    │   │   └── item --> 'a'
                    │   └── 1 --> <ChildPositionUnit>
                    │       └── children --> tuple(1)
                    │           └── 0 --> 'a'
                    └── b --> <PipeUnit count: 2>
                        ├── 0 --> <GetItemUnit>
                        │   └── item --> 'b'
                        └── 1 --> <ChildPositionUnit>
                            └── children --> tuple(1)
                                └── 0 --> 'b'
        """).strip()

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
