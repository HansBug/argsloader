import pytest

from argsloader.base import ParseError, SkippedParseError, MultipleParseError, PValue


@pytest.mark.unittest
class TestBaseException:
    def test_parse_error(self):
        e = ParseError('This is message', 233, PValue(444, ('a', 0)), {'a': 1})
        assert e.message == 'This is message'
        assert e.unit == 233
        assert e.value == PValue(444, ('a', 0))
        assert e.info == {'a': 1}

    def test_parse_error_with_default_info(self):
        e = ParseError('This is message', 233, PValue(444, ('a', 0)))
        assert e.message == 'This is message'
        assert e.unit == 233
        assert e.value == PValue(444, ('a', 0))
        assert e.info is None

    def test_skipped_parse_error(self):
        e = SkippedParseError(233)
        assert e.unit == 233

    def test_multiple_parse_error(self):
        e = MultipleParseError([
            (PValue(233), ParseError('This is message', 233, PValue(444, ('a', 0)), {'a': 1})),
            (PValue(234, ('a', 0)), ParseError('This is 2nd message', 2334, PValue(444, ('a', 0)), {'a': 1})),
        ])
        assert len(e.items) == 2
        assert e.items[0][0] == PValue(233)
        assert e.items[1][0] == PValue(234, ('a', 0))

        assert '(2 errors)' in str(e)
        assert '<root>: ParseError: This is message' in str(e)
        assert '<root>.a.0: ParseError: This is 2nd message' in str(e)

        assert '<MultipleParseError (2 errors)' in repr(e)
        assert '<root>: ParseError: This is message' in repr(e)
        assert '<root>.a.0: ParseError: This is 2nd message' in repr(e)
