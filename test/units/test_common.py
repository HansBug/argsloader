import re
from textwrap import dedent

import pytest

from argsloader.base import ParseError
from argsloader.units import is_, none, yesno, onoff


@pytest.mark.unittest
class TestUnitsCommon:
    def test_is_(self):
        u = is_(1)
        assert u(1)
        with pytest.raises(ParseError) as ei:
            u(2)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        earg0, = err.args
        assert len(err.args) == 1
        assert re.fullmatch('Value expected to be 1\\(0x[\\da-f]+\\), but 2\\(0x[\\da-f]+\\) found\\.', earg0)

    def test_none(self):
        u = none()
        assert u(None) is None
        with pytest.raises(ParseError) as ei:
            u(2)
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        earg0, = err.args
        assert len(err.args) == 1
        assert re.fullmatch('Value expected to be None\\(0x[\\da-f]+\\), but 2\\(0x[\\da-f]+\\) found\\.', earg0)

    def test_yesno(self):
        u = yesno()
        assert u(True) is True
        assert u(False) is False
        assert u(None) is False
        assert u(1) is True
        assert u(0) is False
        assert u('yes') is True
        assert u('Yes') is True
        assert u('YES') is True
        assert u('no') is False
        assert u('  No  ') is False
        assert u('  NO  ') is False
        with pytest.raises(ParseError) as ei:
            u('y e s')
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ("Value expected to be 'yes' or 'no', but 'y e s' found.",)

        assert repr(u).strip() == dedent("""
            <YesNoUnit yes: 'yes', no: 'no'>
        """).strip()

    def test_yesno_diy(self):
        u = yesno('Accept', 'Deny')
        assert u(True) is True
        assert u(False) is False
        assert u(None) is False
        assert u(1) is True
        assert u(0) is False
        assert u('accept') is True
        assert u('Accept') is True
        assert u('ACCEPT') is True
        assert u('deny') is False
        assert u(' Deny    ') is False
        assert u('\t DENY\n\n') is False

        with pytest.raises(ParseError) as ei:
            u('yes')
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ("Value expected to be 'Accept' or 'Deny', but 'yes' found.",)

    def test_yesno_chained(self):
        u = yesno() | yesno('Accept', 'Deny')
        assert u(True) is True
        assert u(False) is False
        assert u(None) is False
        assert u(1) is True
        assert u(0) is False
        assert u('yes') is True
        assert u('Yes') is True
        assert u('YES') is True
        assert u('no') is False
        assert u('  No  ') is False
        assert u('  NO  ') is False
        assert u('accept') is True
        assert u('Accept') is True
        assert u('ACCEPT') is True
        assert u('deny') is False
        assert u(' Deny    ') is False
        assert u('\t DENY\n\n') is False
        with pytest.raises(ParseError) as ei:
            u('y e s')
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ("Value expected to be 'yes' or 'no', but 'y e s' found.",)

    def test_onoff(self):
        u = onoff()
        assert u(True) is True
        assert u(False) is False
        assert u(None) is False
        assert u(1) is True
        assert u(0) is False
        assert u('on') is True
        assert u('On') is True
        assert u('ON') is True
        assert u('off') is False
        assert u('  Off  ') is False
        assert u('  OFF  ') is False
        with pytest.raises(ParseError) as ei:
            u('yes')
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)
        assert err.args == ("Value expected to be 'on' or 'off', but 'yes' found.",)
