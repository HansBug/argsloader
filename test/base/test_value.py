import pytest

from argsloader.base import PValue


@pytest.mark.unittest
class TestBaseValue:
    def test_pvalue(self):
        pval = PValue(233, ('a', 0, 'b'))
        assert pval.value == 233
        assert pval.position == ('a', 0, 'b')

        assert pval == PValue(233, ('a', 0, 'b'))
        assert pval.val(234) == PValue(234, ('a', 0, 'b'))
        assert pval.child('c', 2) == PValue(233, ('a', 0, 'b', 'c', 2))
        assert pval.parent() == PValue(233, ('a', 0))
        assert pval.parent(2) == PValue(233, ('a',))
        assert pval.parent(200) == PValue(233, ())

    def test_pvalue_with_default_position(self):
        pval = PValue(233)
        assert pval.value == 233
        assert pval.position == ()

        assert pval == PValue(233)
        assert pval.val(234) == PValue(234)
        assert pval.child('c', 2) == PValue(233, ('c', 2))
        assert pval.parent() == PValue(233, ())
        assert pval.parent(2) == PValue(233, ())
        assert pval.parent(200) == PValue(233, ())
