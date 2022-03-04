import pytest

from argsloader.units import template, keep, mul, neg


@pytest.mark.unittest
class TestUnitsString:
    def test_template(self):
        u = template(
            '${v} is original data,'
            '${v2} is doubled data,'
            '${v_} is negative data,'
            '${c} is const data',
            dict(v=keep(), v2=mul.by(2), v_=neg(), c=-12)
        )
        assert u(4) == '4 is original data,' \
                       '8 is doubled data,' \
                       '-4 is negative data,' \
                       '-12 is const data'
