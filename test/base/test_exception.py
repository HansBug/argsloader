import pytest

from argsloader.base import ParseError


@pytest.mark.unittest
class TestBaseException:
    def test_parse_exception(self):
        e = ParseError('This is message', 233, 444, {'a': 1})
        assert e.message == 'This is message'
        assert e.unit == 233
        assert e.value == 444
        assert e.info == {'a': 1}

    def test_parse_exception_with_default_info(self):
        e = ParseError('This is message', 233, 444)
        assert e.message == 'This is message'
        assert e.unit == 233
        assert e.value == 444
        assert e.info is None
