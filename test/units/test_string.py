from textwrap import dedent

import pytest

from argsloader.base import ParseError
from argsloader.units import template, keep, mul, neg, regexp


@pytest.mark.unittest
class TestUnitsString:
    def test_template(self):
        u = template(
            '${v} is original data,'
            '${v2} is doubled data,'
            '${v_} is negative data,'
            '${c} is const data',
            v=keep(), v2=mul.by(2), v_=neg(), c=-12
        )
        assert u(4) == '4 is original data,' \
                       '8 is doubled data,' \
                       '-4 is negative data,' \
                       '-12 is const data'
        assert repr(u).strip() == dedent("""
            <TemplateUnit safe: False>
            ├── tmp --> '${v} is original data,${v2} is doubled data,${v_} is negative data,${c} is const data'
            └── vars --> dict(v, v2, v_, c)
                ├── v --> <KeepUnit>
                ├── v2 --> <MulOpUnit>
                │   ├── v1 --> <KeepUnit>
                │   └── v2 --> 2
                ├── v_ --> <NegOpUnit>
                │   └── v1 --> <KeepUnit>
                └── c --> -12
        """).strip()

        u = template(
            '${v} is original data,'
            '${v2} is doubled data,'
            '${v_} is negative data,'
            '${c} is const data',
            v=keep(), v2=mul.by(2), v_=neg()
        )
        with pytest.raises(ParseError) as ei:
            u(4)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, KeyError)
        assert err.args == ("Key 'c' which is required by template is not provided.",)

        u = template.safe(
            '${v} is original data,'
            '${v2} is doubled data,'
            '${v_} is negative data,'
            '${c} is const data',
            v=keep(), v2=mul.by(2), v_=neg()
        )
        assert u(4) == '4 is original data,' \
                       '8 is doubled data,' \
                       '-4 is negative data,' \
                       '${c} is const data'

    def test_regexp_syntax(self):
        u = regexp(r'([\d]{1,3})\.([\d]{1,3})')
        assert repr(u).strip() == dedent("""
            <(X)RegexpProxy>
        """).strip()
        with pytest.raises(SyntaxError):
            u('123.456')

    def test_regexp_match(self):
        # simple match
        u = regexp(r'([\d]{1,3})\.([\d]{1,3})').match
        assert u('123.456') == {0: '123.456', 1: '123', 2: '456'}
        assert u('123.4569203djksfgh') == {0: '123.456', 1: '123', 2: '456'}
        with pytest.raises(ParseError) as ei:
            u('1234.567')
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ("Regular expression '([\\\\d]{1,3})\\\\.([\\\\d]{1,3})' expected, "
                            "but '1234.567' found which is not matched.",)

        assert repr(u).strip() == dedent(r"""
            <RegexpMatchUnit fullmatch: False>
            └── regexp --> '([\\d]{1,3})\\.([\\d]{1,3})'
        """).strip()

        # simple full match
        u = regexp(r'(?P<first>[\d]{1,3})\.(?P<second>[\d]{1,3})').match.full
        assert u('123.456') == {0: '123.456', 1: '123', 2: '456', 'first': '123', 'second': '456'}

        with pytest.raises(ParseError) as ei:
            u('123.4569203djksfgh')
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ("Regular expression '(?P<first>[\\\\d]{1,3})\\\\.(?P<second>[\\\\d]{1,3})' expected, "
                            "but '123.4569203djksfgh' found which is not fully matched.",)

        with pytest.raises(ParseError) as ei:
            u('1234.567')
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ("Regular expression '(?P<first>[\\\\d]{1,3})\\\\.(?P<second>[\\\\d]{1,3})' expected, "
                            "but '1234.567' found which is not fully matched.",)

        assert repr(u).strip() == dedent(r"""
            <RegexpMatchUnit fullmatch: True>
            └── regexp --> '(?P<first>[\\d]{1,3})\\.(?P<second>[\\d]{1,3})'
        """).strip()

    # noinspection DuplicatedCode
    def test_regexp_match_check(self):
        # check only match
        u = regexp(r'([\d]{1,3})\.([\d]{1,3})').match.check
        assert u('123.456') == '123.456'
        assert u('123.4569203djksfgh') == '123.4569203djksfgh'
        with pytest.raises(ParseError) as ei:
            u('1234.567')
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ("Regular expression '([\\\\d]{1,3})\\\\.([\\\\d]{1,3})' expected, "
                            "but '1234.567' found which is not matched.",)

        assert repr(u).strip() == dedent(r"""
            <CheckUnit>
            └── unit --> <RegexpMatchUnit fullmatch: False>
                └── regexp --> '([\\d]{1,3})\\.([\\d]{1,3})'
        """).strip()

        # check only full match
        u = regexp(r'(?P<first>[\d]{1,3})\.(?P<second>[\d]{1,3})').match.full.check
        assert u('123.456') == '123.456'

        with pytest.raises(ParseError) as ei:
            u('123.4569203djksfgh')
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ("Regular expression '(?P<first>[\\\\d]{1,3})\\\\.(?P<second>[\\\\d]{1,3})' expected, "
                            "but '123.4569203djksfgh' found which is not fully matched.",)

        with pytest.raises(ParseError) as ei:
            u('1234.567')
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ("Regular expression '(?P<first>[\\\\d]{1,3})\\\\.(?P<second>[\\\\d]{1,3})' expected, "
                            "but '1234.567' found which is not fully matched.",)

        assert repr(u).strip() == dedent(r"""
            <CheckUnit>
            └── unit --> <RegexpMatchUnit fullmatch: True>
                └── regexp --> '(?P<first>[\\d]{1,3})\\.(?P<second>[\\d]{1,3})'
        """).strip()

    # noinspection DuplicatedCode
    def test_regexp_match_getitem(self):
        u = regexp(r'([\d]{1,3})\.([\d]{1,3})').match[(0, (1, 2))]
        assert u('123.456') == ('123.456', ('123', '456'))
        assert u('123.4569203djksfgh') == ('123.456', ('123', '456'))
        with pytest.raises(ParseError) as ei:
            u('1234.567')
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ("Regular expression '([\\\\d]{1,3})\\\\.([\\\\d]{1,3})' expected, "
                            "but '1234.567' found which is not matched.",)

        u = regexp(r'(?P<first>[\d]{1,3})\.(?P<second>[\d]{1,3})').match.full[(0, ('first', 'second'))]
        assert u('123.456') == ('123.456', ('123', '456'))
        with pytest.raises(ParseError) as ei:
            u('123.4569203djksfgh')
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ("Regular expression '(?P<first>[\\\\d]{1,3})\\\\.(?P<second>[\\\\d]{1,3})' expected, "
                            "but '123.4569203djksfgh' found which is not fully matched.",)

        with pytest.raises(ParseError) as ei:
            u('1234.567')
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ("Regular expression '(?P<first>[\\\\d]{1,3})\\\\.(?P<second>[\\\\d]{1,3})' expected, "
                            "but '1234.567' found which is not fully matched.",)
