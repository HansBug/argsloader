from functools import lru_cache
from operator import itemgetter
from textwrap import indent

from ..base import ParseResult, wrap_exception, ParseError, ResultStatus, PValue
from ..utils import format_tree


def _prefix_indent(prefix, text):
    txt = indent(text, len(prefix) * " ")
    return prefix + txt[len(prefix):]


class _ITreeFormat:
    def _rinfo(self):
        raise NotImplementedError  # pragma: no cover

    def _rcalc(self, is_dispatch):
        attached, _children = self._rinfo()
        attached_content = ", ".join("%s: %s" % (k, repr(v_)) for k, v_ in attached)
        title = f'<{self._cname()}{" " + attached_content if attached else ""}>'
        children = [(k, c) for k, c in _children]
        return title, children

    def __repr__(self):
        return format_tree(self._get_format_unit(self, {}, (), True), itemgetter(0), itemgetter(1))

    @classmethod
    def _cname(cls):
        return cls.__name__

    @classmethod
    def _get_format_unit(cls, v, id_pool, curpath, is_dispatch):
        if isinstance(v, _ITreeFormat):
            title, children = v._rcalc(is_dispatch)
        elif isinstance(v, dict):
            title = f'{type(v).__name__}({", ".join(map(str, v.keys()))})'
            children = [(k, c) for k, c in v.items()]
        elif isinstance(v, (list, tuple)):
            title = f'{type(v).__name__}({len(v)})'
            children = [(i, c) for i, c in enumerate(v)]
        else:
            return repr(v), []

        cs = [cls._get_format_unit(c, id_pool, (*curpath, k), False) for k, c in children]
        return title, [(_prefix_indent(f'{k} --> ', ctitle), cchild)
                       for (k, _), (ctitle, cchild) in zip(children, cs)]


class _UnitModel(_ITreeFormat):
    def __call__(self, v):
        raise NotImplementedError  # pragma: no cover

    def call(self, v, err_mode='ALL'):
        raise NotImplementedError  # pragma: no cover

    def log(self, v) -> ParseResult:
        raise NotImplementedError  # pragma: no cover

    @property
    def validity(self) -> 'BaseUnit':
        raise NotImplementedError  # pragma: no cover


class UncompletedUnit(_UnitModel):
    """
    Overview:
        Uncompleted unit class, used when some unit structure is not completed.
    """

    def _fail(self):
        """
        Fail method, should raise error when this uncompleted unit is used.

        :raises SyntaxError: Unit syntax error.
        """
        raise NotImplementedError  # pragma: no cover

    def __call__(self, v):
        """
        Calculate with given value.

        .. warning::
            This will fail due to its incompleteness.

        :param v: Input value.
        :return: Output value.
        :raises SyntaxError: Unit syntax error.
        """
        return self._fail()

    def call(self, v, err_mode='ALL'):
        """
        Calculate with given value, similar to :meth:`__call__`.

        .. warning::
            This will fail due to its incompleteness.

        :param v: Input value.
        :param err_mode: Error mode, see :class:`argsloader.base.result.ErrMode`.
        :raises SyntaxError: Unit syntax error.
        """
        return self._fail()

    def log(self, v) -> ParseResult:
        """
        Get full log of this parsing process.

        .. warning::
            This will fail due to its incompleteness.

        :param v: Input value.
        :raises SyntaxError: Unit syntax error.
        """
        return self._fail()

    @property
    def validity(self) -> 'BaseUnit':
        """
        Validity of this unit.

        See: :func:`argsloader.units.utils.validity`.

        .. warning::
            This will fail due to its incompleteness.
        """
        return self._fail()

    @classmethod
    def _cname(cls):
        return f'(X){cls.__name__}'

    def _rinfo(self):
        raise NotImplementedError  # pragma: no cover


class UnitProcessProxy:
    """
    Overview:
        Proxy class, used to create result object.
    """

    def __init__(self, unit: 'BaseUnit', v: PValue):
        """
        Constructor of class :class:`argsloader.units.base.UnitProcessProxy`.

        :param unit: Unit object.
        :param v: ``PValue`` object.
        """
        self.__unit = unit
        self.__v = v

    def success(self, res: PValue, children=None) -> ParseResult:
        """
        Build a success result.

        :param res: ``PValue`` result object.
        :param children: Children objects.
        :return: Success parse result.
        """
        return ParseResult(
            self.__v, self.__unit,
            ResultStatus.SUCCESS, res, None, children
        )

    def error(self, err, children=None) -> ParseResult:
        """
        Build an error result.

        :param err: Error object, will be transformed to :class:`argsloader.base.exception.ParseError` if \
            it is not yet.
        :param children: Children objects.
        :return: Error parse result.
        """
        if err is not None and not isinstance(err, ParseError):
            err = wrap_exception(err, self.__unit, self.__v)
        return ParseResult(
            self.__v, self.__unit,
            ResultStatus.ERROR, None, err, children
        )

    def skipped(self) -> ParseResult:
        """
        Build a skipped result.

        :return: Skipped parse result.
        """
        return ParseResult(
            None, self.__unit,
            ResultStatus.SKIPPED, None, None, None
        )


@lru_cache()
def _get_ops():
    from .operator import _cpipe, _cand, _cor
    return _cpipe, _cand, _cor


class BaseUnit(_UnitModel):
    def _process(self, v: PValue) -> ParseResult:
        """
        Protected process method.

        :param v: ``PValue`` input object.
        :return: Parse result object.
        """
        return self._easy_process(v, UnitProcessProxy(self, v))

    def _easy_process(self, v: PValue, proxy: UnitProcessProxy) -> ParseResult:
        """
        Easy process method, ``proxy`` can be used to quickly build parse result object.

        :param v: ``PValue`` object.
        :param proxy: Proxy object.
        :return: Parse result object.
        """
        raise NotImplementedError  # pragma: no cover

    def _skip(self, v: PValue) -> ParseResult:
        """
        Create a skipped result

        :param v: ``PValue`` object.
        :return: Skipped parse result object.
        """
        return UnitProcessProxy(self, v).skipped()

    def __call__(self, v):
        """
        Calculate with given value.

        :param v: Input value.
        :return: Output value.
        :raises ParseError: Parse error.
        """
        return self.call(v, 'FIRST')

    def call(self, v, err_mode='ALL'):
        """
        Calculate with given value, similar to :meth:`__call__`.

        :param v: Input value.
        :param err_mode: Error mode, see :class:`argsloader.base.result.ErrMode`, default is ``ALL``.
        :return: Output value.
        :raises ParseError: Parse error.
        :raises MultipleParseError: Indexed parsed error, will be raised when ``ALL`` mode is used.
        """
        return self._process(PValue(v, ())).act(err_mode)

    def log(self, v) -> ParseResult:
        """
        Get full log of this parsing process.

        :param v: Input value.
        :return: Parse result.
        """
        return self._process(PValue(v, ()))

    @property
    def validity(self) -> 'BaseUnit':
        """
        Validity of this unit.

        See: :func:`argsloader.units.utils.validity`.
        """
        from .utils import validity
        return validity(self)

    def __rshift__(self, other) -> 'BaseUnit':
        """
        Build pipe within units, like ``self >> other``.

        See :func:`argsloader.units.operator.pipe`.

        :param other: Another unit.
        :return: Piped unit.
        """
        pipe, _, _ = _get_ops()
        return pipe(self, _to_unit(other))

    def __rrshift__(self, other) -> 'BaseUnit':
        """
        Right version of :meth:`__rshift__`, like ``other >> self``.

        :param other: Another unit.
        :return: Piped unit.
        """
        return _to_unit(other) >> self

    def __and__(self, other) -> 'BaseUnit':
        """
        Build and-liked unit within units, like ``self & other``.

        See :func:`argsloader.units.operator.and_`.

        :param other: Another unit.
        :return: And-linked unit.
        """
        _, and_, _ = _get_ops()
        return and_(self, _to_unit(other))

    def __rand__(self, other) -> 'BaseUnit':
        """
        Right version of :meth:`__and__`, like ``other & self``.

        :param other: Another unit.
        :return: And-linked unit.
        """
        return _to_unit(other) & self

    def __or__(self, other) -> 'BaseUnit':
        """
        Build or-liked unit within units, like ``self | other``.

        See :func:`argsloader.units.operator.or_`.

        :param other: Another unit.
        :return: Or-linked unit.
        """
        _, _, or_ = _get_ops()
        return or_(self, _to_unit(other))

    def __ror__(self, other) -> 'BaseUnit':
        """
        Right version of :meth:`__or__`, like ``other | self``.

        See :func:`argsloader.units.operator.or_`.

        :param other: Another unit.
        :return: Or-linked unit.
        """
        return _to_unit(other) | self

    def _rinfo(self):
        raise NotImplementedError  # pragma: no cover


class ValueUnit(BaseUnit):
    """
    Overview:
        Raw value unit.
    """

    def __init__(self, value):
        """
        Constructor of class :class:`argsloader.units.base.ValueUnit`.

        :param value: Raw value.
        """
        self._value = value

    def _easy_process(self, v: PValue, proxy: UnitProcessProxy) -> ParseResult:
        return proxy.success(v.val(self._value))

    def _rcalc(self, is_dispatch):
        if is_dispatch:
            return BaseUnit._rcalc(self, is_dispatch)
        else:
            return repr(self._value), []

    def _rinfo(self):
        return [], [('value', self._value)]


def raw(v) -> ValueUnit:
    """
    Raw value unit.

    :param v: Original value.
    :return: raw value unit.
    """
    return ValueUnit(v)


def _to_unit(v) -> BaseUnit:
    from .build import UnitBuilder
    if isinstance(v, UncompletedUnit):
        getattr(v, '_fail')()
    elif isinstance(v, BaseUnit):
        return v
    elif isinstance(v, UnitBuilder):
        return v.unit
    else:
        from .func import _FUNC_TYPES
        if isinstance(v, _FUNC_TYPES):
            from .func import proc
            return proc(v)
        else:
            return raw(v)
