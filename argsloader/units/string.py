import re
from typing import Mapping, Any

from hbutils.collection import nested_map
from hbutils.string import env_template, truncate

from .base import _to_unit, UncompletedUnit
from .build import CalculateUnit
from .structure import getitem_, struct
from .utils import check, CheckUnit

try:
    from re import Pattern
except ImportError:
    Pattern = type(re.compile(''))


class TemplateUnit(CalculateUnit):
    """
    Overview:
        Unit for templating string.
    """
    __names__ = ('tmp', 'vars')
    __errors__ = (KeyError,)

    def __init__(self, tmp, variables: Mapping[str, Any], safe: bool):
        """
        Constructor of :class:`TemplateUnit`.

        :param tmp: Template string.
        :param variables: Variable objects.
        :param safe: Safe mode or not.
        """
        self._safe = safe
        CalculateUnit.__init__(self, tmp, {k: _to_unit(v) for k, v in variables.items()})

    def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
        try:
            return env_template(pres['tmp'], pres['vars'], safe=self._safe)
        except KeyError as err:
            key, = err.args
            raise KeyError(f'Key {repr(key)} which is required by template is not provided.')

    def _rinfo(self):
        _, children = CalculateUnit._rinfo(self)
        return [('safe', self._safe)], children


def _template_safe(_s_template, **vars_) -> TemplateUnit:
    return TemplateUnit(_s_template, vars_, True)


def template(_s_template, **vars_) -> TemplateUnit:
    """
    Overview:
        Create a string, based on a template and several variables.

    :param _s_template: Template string.
    :param vars_: Variables to be used.
    :return: A template based unit.

    Examples::
        >>> from argsloader.units import keep, neg, mul, template
        >>> u = template(
        ...     '${v} is original data,'
        ...     '${v2} is doubled data,'
        ...     '${v_} is negative data,'
        ...     '${c} is const data',
        ...     v=keep(), v2=mul.by(2), v_=neg(), c=-12
        ... )
        >>> u(4)
        '4 is original data,8 is doubled data,-4 is negative data,-12 is const data'

    .. note::
        When function :func:`template` is used, the safe mode is disabled in default. It means when one of the \
        required variable's data is not given, a ``KeyError`` will be raised. For example,

        >>> u = template(
        ...     '${v} is original data,'
        ...     '${v2} is doubled data,'
        ...     '${v_} is negative data,'
        ...     '${c} is const data',
        ...     v=keep(), v2=mul.by(2), v_=neg()  # c is missing
        ... )
        >>> u(4)
        KeyParseError: "Key 'c' which is required by template is not provided."

        In the abovementioned case, if you need to just keep the missing string, you can enable the safe mode with \
        ``template.safe``. For example,

        >>> u = template.safe(
        ...     '${v} is original data,'
        ...     '${v2} is doubled data,'
        ...     '${v_} is negative data,'
        ...     '${c} is const data',
        ...     v=keep(), v2=mul.by(2), v_=neg()  # c is missing
        ... )
        >>> u(4)
        '4 is original data,8 is doubled data,-4 is negative data,${c} is const data'
    """
    return TemplateUnit(_s_template, vars_, False)


template.safe = _template_safe


class RegexpMatchUnit(CalculateUnit):
    """
    Overview:
        Unit for regular expression matching.
    """
    __names__ = ('regexp',)
    __errors__ = (ValueError,)

    def __init__(self, r, fullmatch: bool = False):
        """
        Constructor of :class:`RegexpMatchUnit`.

        :param r: Regular expression string or pattern.
        :param fullmatch: Fully match required or not, default is ``False``.
        """
        self._regexp = r
        self._fullmatch = fullmatch
        CalculateUnit.__init__(self, r)

    @property
    def full(self) -> 'RegexpMatchUnit':
        """
        :return: A :class:`RegexpMatchUnit` with fully-match option enabled.
        """
        return self.__class__(self._regexp, True)

    @property
    def check(self) -> 'CheckUnit':
        """
        :return: A :class:`argsloader.units.utils.CheckUnit` which only check the match or not.
        """
        return check(self)

    def __getitem__(self, struct_):
        """
        :param struct_: The expected structure.
        :return: A :class:`argsloader.units.operator.PipeUnit` which can combine the grouped data together.
        """
        return self >> struct(nested_map(lambda x: getitem_(x, offset=False), struct_))

    def _calculate(self, v: str, pres: Mapping[str, Any]):
        r = pres['regexp']
        if not isinstance(r, Pattern):
            r = re.compile(r)

        mfunc = r.fullmatch if self._fullmatch else r.match
        match = mfunc(v)
        if match:
            return {
                0: match.group(0),
                **{i + 1: content for i, content in enumerate(match.groups())},
                **match.groupdict(),
            }
        else:
            raise ValueError(f'Regular expression {repr(r.pattern)} expected, '
                             f'but {truncate(repr(v))} found which is '
                             f'not {"fully " if self._fullmatch else ""}matched.')

    def _rinfo(self):
        _, children = super()._rinfo()
        return [('fullmatch', self._fullmatch)], children


class RegexpProxy(UncompletedUnit):
    """
    Overview:
        Proxy class for regular expression units' building.

    .. note::
        This class is only used for building unit, which means it can not be used like unit \
        because of its incompleteness.
    """

    def __init__(self, r) -> None:
        """
        Constructor of :class:`RegexpProxy`.

        :param r: Regular expression string or pattern.
        """
        UncompletedUnit.__init__(self)
        self._regexp = r

    def _fail(self):
        raise SyntaxError('Uncompleted regular expression unit - no command is given.')

    def _rinfo(self):
        return [], []

    @property
    def match(self):
        """
        :return: A :class:`RegexpMatchUnit` with fully-match and check-only options disabled.
        """
        return RegexpMatchUnit(self._regexp, False)


def regexp(r) -> RegexpProxy:
    """
    Overview:

    :param r: Regular expression string or pattern. If string is given, it will be compiled inside.
    :return: A :class:`RegexpProxy` object.

    Examples::
        - Simple match

        >>> from argsloader.units import regexp
        >>> u = regexp('([a-z0-9_]+)@([a-z0-9_\\.]+)').match
        >>> u('mymail@gmail.com')
        {0: 'mymail@gmail.com', 1: 'mymail', 2: 'gmail.com'}
        >>> u('mymail@gmail.com  here is other text')
        {0: 'mymail@gmail.com', 1: 'mymail', 2: 'gmail.com'}
        >>> u('mymail_gmail.com')
        ValueParseError: Regular expression '([a-z0-9_]+)@([a-z0-9_\\.]+)' expected, but 'mymail_gmail.com' found which is not matched.

        - Check only

        >>> u = regexp('([a-z0-9_]+)@([a-z0-9_\\.]+)').match.check
        >>> u('mymail@gmail.com')
        'mymail@gmail.com'
        >>> u('mymail@gmail.com  here is other text')
        'mymail@gmail.com  here is other text'
        >>> u('mymail_gmail.com')
        ValueParseError: Regular expression '([a-z0-9_]+)@([a-z0-9_\\.]+)' expected, but 'mymail_gmail.com' found which is not matched.

        - Fully match

        >>> u = regexp('([a-z0-9_]+)@([a-z0-9_\\.]+)').match.full
        >>> u('mymail@gmail.com')
        {0: 'mymail@gmail.com', 1: 'mymail', 2: 'gmail.com'}
        >>> u('mymail@gmail.com  here is other text')
        ValueParseError: Regular expression '([a-z0-9_]+)@([a-z0-9_\\.]+)' expected, but 'mymail@gmail.com here is other text' found which is not fully matched.

        - Fully match, check only

        >>> u = regexp('([a-z0-9_]+)@([a-z0-9_\\.]+)').match.full.check
        >>> u('mymail@gmail.com')
        'mymail@gmail.com'
        >>> u('mymail@gmail.com  here is other text')
        ValueParseError: Regular expression '([a-z0-9_]+)@([a-z0-9_\\.]+)' expected, but 'mymail@gmail.com here is other text' found which is not fully matched.

        - Match with named group

        >>> u = regexp('(?P<username>[a-z0-9_]+)@(?P<domain>[a-z0-9_\\.]+)').match
        >>> u('mymail@gmail.com')
        {0: 'mymail@gmail.com', 1: 'mymail', 2: 'gmail.com', 'username': 'mymail', 'domain': 'gmail.com'}
        >>> u('mymail@gmail.com  here is other text')
        {0: 'mymail@gmail.com', 1: 'mymail', 2: 'gmail.com', 'username': 'mymail', 'domain': 'gmail.com'}
        >>> u('mymail_gmail.com')
        ValueParseError: Regular expression '(?P<username>[a-z0-9_]+)@(?P<domain>[a-z0-9_\\.]+)' expected, but 'mymail_gmail.com' found which is not matched.

        - Get data from matching result

        >>> from argsloader.units import regexp
        >>> u = regexp('([a-z0-9_]+)@([a-z0-9_\\.]+)').match.full[(0, {'u': 1, 'd': 2})]
        >>> u('mymail@gmail.com')
        ('mymail@gmail.com', {'u': 'mymail', 'd': 'gmail.com'})
        >>>
        >>> u = regexp('(?P<username>[a-z0-9_]+)@(?P<domain>[a-z0-9_\\.]+)').match[(0, ('username', 'domain'))]
        >>> u('mymail@gmail.com')
        ('mymail@gmail.com', ('mymail', 'gmail.com'))

    .. warning::
        The object which function :func:`regexp` returned is only a :class:`RegexpProxy` object, \
        which is only used for building unit and can not be used like other functions.

    .. note::
        The other functions like ``re.find`` or ``re.search`` will be added later.
    """
    return RegexpProxy(r)
