from typing import Mapping, Any

from inflection import underscore

from .base import UnitProcessProxy
from .build import CalculateUnit, BaseUnit
from ..base import PValue, ParseResult


class IsUnit(CalculateUnit):
    """
    Overview:
        Unit for ``is`` calculation.
    """
    __names__ = ('target',)
    __errors__ = (ValueError,)

    def __init__(self, target):
        """
        Constructor of :class:`IsUnit`.

        :param target: Target for calculation.
        """
        CalculateUnit.__init__(self, target)

    def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
        target = pres['target']
        if v is target:
            return v
        else:
            raise ValueError(f'Value expected to be {repr(target)}({hex(id(target))}), '
                             f'but {repr(v)}({hex(id(v))}) found.')


def is_(v) -> IsUnit:
    """
    Overview:
        Check if the given object is the same object as ``v``.

    :param v: Unit or value to be checked.
    :return: A :class:`IsUnit` object.

    Examples::
        >>> from argsloader.units import is_
        >>> u = is_(1)
        >>> u(1)  # 1 is 1, int is immutable in python
        1
        >>> u(2)  # 2 is 1
        ValueParseError: Value expected to be 1(0x7fb7799546c0), but 2(0x7fb7799546e0) found.
        >>> u(None)
        ValueParseError: Value expected to be 1(0x7fb7799546c0), but None(0x7fb77990a110) found.
    """
    return IsUnit(v)


def none():
    """
    Overview:
        Check if the given value is none.

    Examples::
        >>> from argsloader.units import none
        >>> u = none()
        >>> u(None)  # None is None
        >>> u(2)  # 2 is None
        ValueParseError: Value expected to be None(0x7fb77990a110), but 2(0x7fb7799546e0) found.
    """
    return is_(None)


def _string_formal(s: str):
    return underscore(s.strip()).lower()


class YesNoUnit(BaseUnit):
    """
    Overview:
        Unit for parsing yes or no option.
    """

    def __init__(self, yes='yes', no='no'):
        """
        Constructor of :class:`YesNoUnit`.

        :param yes: Yes string.
        :param no: No string.
        """
        self._syes = yes
        self._sno = no

    def _easy_process(self, v: PValue, proxy: UnitProcessProxy) -> ParseResult:
        if isinstance(v.value, str):
            fv = _string_formal(v.value)
            if fv == _string_formal(self._syes):
                return proxy.success(v.val(True))
            elif fv == _string_formal(self._sno):
                return proxy.success(v.val(False))
            else:
                return proxy.error(ValueError(f'Value expected to be {repr(self._syes)} or {repr(self._sno)}, '
                                              f'but {repr(v.value)} found.'))
        else:
            return proxy.success(v.val(bool(v.value)))

    def _rinfo(self):
        return [('yes', self._syes), ('no', self._sno)], []


def yesno(yes='yes', no='no') -> YesNoUnit:
    """
    Overview:
        Parse yes-or-no option.

    :param yes: Yes string, default is ``yes``.
    :param no: No string, default is ``no``.
    :return: A :class:`YesNoUnit` object.

    Examples::
        - Simple Usage

        >>> from argsloader.units import yesno
        >>> u = yesno()
        >>> u('yes')
        True
        >>> u('no')
        False
        >>> u(True)
        True
        >>> u(False)
        False
        >>> u(1)
        True
        >>> u(0)
        False
        >>> u('xxx')
        ValueParseError: Value expected to be 'yes' or 'no', but 'xxx' found.

        - Self-defined tags

        >>> from argsloader.units import yesno
        >>> u = yesno('Accept', 'Decline')
        >>> u('accept')
        True
        >>> u('decline')
        False
        >>> u(True)
        True
        >>> u(False)
        False
        >>> u(1)
        True
        >>> u(0)
        False
        >>> u('yes')
        ValueParseError: Value expected to be 'Accept' or 'Decline', but 'yes' found.

    .. note::
        If you need to parse from multiple pairs of yes and no tags, you can simply chain them \
        together with ``|`` operator.

        >>> from argsloader.units import yesno
        >>> u = yesno() | yesno('Accept', 'Decline')
        >>> u('yes')
        True
        >>> u('NO')
        False
        >>> u('accept')
        True
        >>> u('decline')
        False
        >>> u('xxx')
        ValueParseError: Value expected to be 'yes' or 'no', but 'xxx' found.
    """
    return YesNoUnit(yes, no)


def onoff():
    """
    Overview:
        Parse on-or-off option.

        The same as ``yesno('on', 'off')``, see :func:`yesno`.
    """
    return yesno('on', 'off')
