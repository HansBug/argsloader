import pytest

from argsloader.base import ParseError, SkippedParseError, MultipleParseError, PValue, wrap_exception, \
    wrap_exception_class


@pytest.mark.unittest
class TestBaseException:
    def test_parse_error(self):
        e = ParseError('This is message', 233, PValue(444, ('a', 0)), {'a': 1})
        assert e.message == 'This is message'
        assert e.unit == 233
        assert e.value == PValue(444, ('a', 0))
        assert e.info == {'a': 1}

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

    def test_wrap_exception(self):
        err = wrap_exception(ValueError('sdkfjlsd'), 1, 2)
        assert isinstance(err, ValueError)
        assert isinstance(err, ParseError)
        assert err.message == 'sdkfjlsd'
        assert err.unit == 1
        assert err.value == 2
        assert err.info == ()

        err = wrap_exception(TypeError('sdkfjlsd', 5, 6, 7, 8), 1, 2)
        assert isinstance(err, TypeError)
        assert isinstance(err, ParseError)
        assert err.message == 'sdkfjlsd'
        assert err.unit == 1
        assert err.value == 2
        assert err.info == (5, 6, 7, 8)

    def test_wrap_exception_class(self):
        errcls = wrap_exception_class(ValueError)
        assert isinstance(errcls, type)
        assert issubclass(errcls, ParseError)
        assert issubclass(errcls, ValueError)
        assert errcls.__name__ == 'ValueParseError'

        class _MyException(Exception):
            pass

        errcls = wrap_exception_class(_MyException)
        assert isinstance(errcls, type)
        assert issubclass(errcls, ParseError)
        assert issubclass(errcls, _MyException)
        assert errcls.__name__ == '_MyParseException'

        class _MyFxxkingSignalClass(Exception):
            pass

        with pytest.raises(NameError):
            _ = wrap_exception_class(_MyFxxkingSignalClass)
