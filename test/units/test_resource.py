from textwrap import dedent

import pytest

from argsloader.base import ParseError
from argsloader.units import timespan, memory_


@pytest.mark.unittest
class TestUnitsResource:
    def test_timespan(self):
        u = timespan()
        assert u('1h') == 3600.0
        assert u('2d4h33m98s') == 189278.0
        assert repr(u).strip() == dedent("""
            <TimespanUnit unit: <TimeScale.SECOND: 1.0>>
        """).strip()

    def test_timespan_scale(self):
        u = timespan.nano()
        assert u('1h') == 3600.0 * 1e9
        assert u('2d4h33m98s') == 189278.0 * 1e9

        u = timespan.micro()
        assert u('1h') == 3600.0 * 1e6
        assert u('2d4h33m98s') == 189278.0 * 1e6

        u = timespan.milli()
        assert u('1h') == 3600.0 * 1e3
        assert u('2d4h33m98s') == 189278.0 * 1e3

        u = timespan.seconds()
        assert u('1h') == 3600.0
        assert u('2d4h33m98s') == 189278.0

        u = timespan.minutes()
        assert u('1h') == 60.0
        assert abs(u('2d4h33m98s') - 3154.633333333333) < 1e-5

        u = timespan.hours()
        assert u('1h') == 1.0
        assert abs(u('2d4h33m98s') - 52.577222222222225) < 1e-5

        u = timespan.days()
        assert abs(u('1h') - 0.041666666666666664) < 1e-5
        assert abs(u('2d4h33m98s') - 2.1907175925925926) < 1e-5

    def test_memory_(self):
        u = memory_()
        assert u(100) == 100
        assert u(19824.0) == 19824
        assert u('5mb') == 5000000.0
        assert u('   7   gib') == 7516192768.0
        with pytest.raises(ParseError) as ei:
            u('sdjkflksdj')
        err = ei.value
        assert isinstance(err, ParseError)
        assert isinstance(err, ValueError)

        assert repr(u).strip() == dedent("""
            <MemoryUnit unit: <MemoryScale.B: 1.0>>
        """).strip()

    def test_memory_scale(self):
        u = memory_.bytes()
        assert u(100) == 100
        assert u(19824.0) == 19824
        assert u('5mb') == 5000000.0
        assert u('   7   gib') == 7516192768.0

        u = memory_.KB()
        assert abs(u(100) - 0.1) < 1e-8
        assert abs(u(19824.0) - 19.824) < 1e-8
        assert abs(u('5mb') - 5000.0) < 1e-8
        assert abs(u('   7   gib') - 7516192.768) < 1e-8

        u = memory_.KiB()
        assert abs(u(100) - 0.09765625) < 1e-8
        assert abs(u(19824.0) - 19.359375) < 1e-8
        assert abs(u('5mb') - 4882.8125) < 1e-8
        assert abs(u('   7   gib') - 7340032.0) < 1e-8

        u = memory_.MB()
        assert abs(u(100) - 0.0001) < 1e-8
        assert abs(u(19824.0) - 0.019824) < 1e-8
        assert abs(u('5mb') - 5.0000) < 1e-8
        assert abs(u('   7   gib') - 7516.192768) < 1e-8

        u = memory_.MiB()
        assert abs(u(100) - 9.5367431640625e-05) < 1e-8
        assert abs(u(19824.0) - 0.0189056396484375) < 1e-8
        assert abs(u('5mb') - 4.76837158203125) < 1e-8
        assert abs(u('   7   gib') - 7168) < 1e-8

        u = memory_.GB()
        assert abs(u(19824.0) - 0.000019824) < 1e-8
        assert abs(u('5mb') - 0.0050000) < 1e-8
        assert abs(u('   7   gib') - 7.516192768) < 1e-8

        u = memory_.GiB()
        assert abs(u(19824.0) - 1.8462538719177246e-05) < 1e-8
        assert abs(u('5mb') - 0.004656612873077393) < 1e-8
        assert abs(u('   7   gib') - 7.0) < 1e-8

        u = memory_.TB()
        assert abs(u('23978GB') - 23.978) < 1e-8

        u = memory_.TiB()
        assert abs(u('23978GB') - 21.807863959111273) < 1e-8
