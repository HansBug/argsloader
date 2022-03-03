import pytest

from argsloader.base import ResultStatus, ParseResult, PValue, wrap_exception, raw_res, SkippedParseError, ParseError, \
    MultipleParseError, ParseResultChildProxy


@pytest.mark.unittest
class TestBaseResult:
    def test_result_status(self):
        assert ResultStatus.loads('skipped') == ResultStatus.SKIPPED
        assert ResultStatus.loads('success') == ResultStatus.SUCCESS
        assert ResultStatus.loads('error') == ResultStatus.ERROR

        assert not ResultStatus.SKIPPED.processed
        assert not ResultStatus.SKIPPED.valid
        assert ResultStatus.SUCCESS.processed
        assert ResultStatus.SUCCESS.valid
        assert ResultStatus.ERROR.processed
        assert not ResultStatus.ERROR.valid

    def test_parse_result_common(self):
        r = ParseResult(PValue(233, ()), 'this is unit', 'success', PValue(234, ()), None)
        assert r.input == PValue(233, ())
        assert r.unit == 'this is unit'
        assert r.status == ResultStatus.SUCCESS
        assert r.result == PValue(234, ())
        assert r.error is None

    def test_parse_result_repr(self):
        val_, unit_ = PValue(233, ()), 'this is unit'

        r = ParseResult(val_, unit_, 'success', PValue(234, ()), None)
        assert repr(r) == '<ParseResult input: <PValue value: 233, position: ()>, ' \
                          'status: SUCCESS, result: <PValue value: 234, position: ()>>'

        r = ParseResult(val_, unit_, 'error', None,
                        wrap_exception(ValueError('errmsg', 1, None, [3, 4]), unit_, val_))
        assert repr(r) == '<ParseResult input: <PValue value: 233, position: ()>, status: ERROR, error: errmsg>'

        r = ParseResult(None, unit_, 'skipped', None, None)
        assert repr(r) == '<ParseResult status: SKIPPED>'

    def test_parse_result_children(self):
        val_, unit_ = PValue(233, ()), 'this is unit'

        r = ParseResult(val_, unit_, 'success', PValue(234, ()), None, [
            {'a': 1, 'b': raw_res([3, 4]), 'c': {'x': 1}},
            raw_res({'a': 1, 'b': 3}),
            [3, 5, 7, raw_res({'a': 11})]
        ])
        assert r[0]['a'] == 1
        assert r[0]['b'] == [3, 4]
        assert r[1] == {'a': 1, 'b': 3}
        assert r[2][3] == {'a': 11}
        assert 0 in r
        assert 20 not in r
        assert 'a' in r[0]
        assert 'z' not in r[0]
        assert set(r.keys()) == {0, 1, 2}
        assert set(r[0].keys()) == {'a', 'b', 'c'}
        assert sorted(r.items()) == [
            (0, ParseResultChildProxy({'a': 1, 'b': raw_res([3, 4]), 'c': {'x': 1}})),
            (1, {'a': 1, 'b': 3}),
            (2, ParseResultChildProxy([3, 5, 7, raw_res({'a': 11})])),
        ]
        assert sorted(r[2].items()) == [
            (0, 3),
            (1, 5),
            (2, 7),
            (3, {'a': 11}),
        ]
        assert sorted(r[0].items()) == [
            ('a', 1),
            ('b', [3, 4]),
            ('c', ParseResultChildProxy({'x': 1})),
        ]

        with pytest.raises(ValueError):
            _ = ParseResult(val_, unit_, 'success', PValue(234, ()), None, 'dsfj')

    def test_parse_result_no_children(self):
        val_, unit_ = PValue(233, ()), 'this is unit'
        r = ParseResult(val_, unit_, 'success', PValue(234, ()), None)
        with pytest.raises(KeyError):
            _ = r[0]
        assert 'a' not in r
        assert set(r.keys()) == set()
        assert sorted(r.items()) == []

    def test_parse_result_act_1(self):
        val_, unit_ = PValue(233, ()), 'this is unit'

        r = ParseResult(val_, unit_, 'success', PValue(234, ()), None)
        assert r.act('all') == 234

        r = ParseResult(val_, unit_, 'skipped', None, None)
        with pytest.raises(SkippedParseError):
            r.act('all')

        r = ParseResult(val_, unit_, 'error', None, wrap_exception(ValueError('errmsg'), unit_, val_))
        with pytest.raises(ParseError) as ei:
            r.act('first')
        assert isinstance(ei.value, ValueError)
        assert ei.value.message == 'errmsg'

        with pytest.raises(ParseError) as ei:
            r.act('try_all')
        assert isinstance(ei.value, ValueError)
        assert ei.value.message == 'errmsg'

        with pytest.raises(MultipleParseError) as ei:
            r.act('all')
        err: MultipleParseError = ei.value
        assert len(err.items) == 1

        r2 = ParseResult(val_, unit_, 'error', None, None, {
            'a': r,
            'c': [{'b': r, }]
        })
        with pytest.raises(ParseError) as ei:
            r2.act('first')
        assert isinstance(ei.value, ValueError)
        assert ei.value.message == 'errmsg'

        with pytest.raises(MultipleParseError) as ei:
            r2.act('try_all')
        err: MultipleParseError = ei.value
        assert len(err.items) == 2

        with pytest.raises(MultipleParseError) as ei:
            r2.act('all')
        err: MultipleParseError = ei.value
        assert len(err.items) == 2
