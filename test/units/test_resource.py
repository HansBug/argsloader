from textwrap import dedent

import pytest

from argsloader.units import timespan


@pytest.mark.unittest
class TestUnitsResource:
    def test_timespan(self):
        u = timespan
        assert u('1h') == 3600.0
        assert u('2d4h33m98s') == 189278.0
        assert repr(u).strip() == dedent("""
            <TimespanUnit unit: <TimeScale.SECOND: 1.0>>
        """).strip()

    def test_timespan_scale(self):
        u = timespan.nano
        assert u('1h') == 3600.0 * 1e9
        assert u('2d4h33m98s') == 189278.0 * 1e9

        u = timespan.micro
        assert u('1h') == 3600.0 * 1e6
        assert u('2d4h33m98s') == 189278.0 * 1e6

        u = timespan.milli
        assert u('1h') == 3600.0 * 1e3
        assert u('2d4h33m98s') == 189278.0 * 1e3

        u = timespan.seconds
        assert u('1h') == 3600.0
        assert u('2d4h33m98s') == 189278.0

        u = timespan.minutes
        assert u('1h') == 60.0
        assert abs(u('2d4h33m98s') - 3154.633333333333) < 1e-5

        u = timespan.hours
        assert u('1h') == 1.0
        assert abs(u('2d4h33m98s') - 52.577222222222225) < 1e-5

        u = timespan.days
        assert abs(u('1h') - 0.041666666666666664) < 1e-5
        assert abs(u('2d4h33m98s') - 2.1907175925925926) < 1e-5
