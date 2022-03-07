from functools import lru_cache
from operator import itemgetter
from textwrap import indent
from typing import Mapping, Any

from hbutils.collection import nested_map
from hbutils.string import plural_word

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

    def call(self, v, err_mode='first'):
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

    def call(self, v, err_mode='first'):
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
    from .operator import pipe, and_, or_
    return pipe, and_, or_


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
        return self.call(v)

    def call(self, v, err_mode='first'):
        """
        Calculate with given value, similar to :meth:`__call__`.

        :param v: Input value.
        :param err_mode: Error mode, see :class:`argsloader.base.result.ErrMode`.
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
    if isinstance(v, UncompletedUnit):
        getattr(v, '_fail')()
    if isinstance(v, BaseUnit):
        return v
    else:
        return raw(v)


class TransformUnit(BaseUnit):
    """
    Overview:
        Common transform unit.
    """
    __errors__ = ()
    __names__ = ()

    def __init__(self, *values):
        """
        Constructor of class :class:`argsloader.units.base.TransformUnit`.

        :param values: Values need to be pre-processed, should be mapped one-to-one with ``__names__``.
        """
        if len(self.__names__) != len(values):
            raise TypeError(f'{type(self).__name__} should accept {plural_word(len(self.__names__), "word")}, '
                            f'but {plural_word(len(values), "word")} found.')

        self._values = nested_map(_to_unit, tuple(values))

    def _transform(self, v: PValue, pres: Mapping[str, Any]) -> PValue:
        """
        Transform method.

        :param v: Original ``PValue`` object.
        :param pres: Pre-processed values.
        :return: Returned ``PValue`` object.
        :raises Exception: Raised exception which is instance of ``__errors__`` will be processed.
        """
        raise NotImplementedError  # pragma: no cover

    def _easy_process(self, v: PValue, proxy: UnitProcessProxy) -> ParseResult:
        ovalues, valid = dict(zip(self.__names__, self._values)), True

        def _recursion(ov):
            nonlocal valid

            if isinstance(ov, dict):
                vs, rs = {}, {}
                for name_, iv in ov.items():
                    v_, res = _recursion(iv)
                    vs[name_] = v_
                    rs[name_] = res
                tp = type(ov)
                return tp(vs), tp(rs)
            elif isinstance(ov, (list, tuple)):
                vs, rs = [], []
                for iv in ov:
                    v_, res = _recursion(iv)
                    vs.append(v_)
                    rs.append(res)
                tp = type(ov)
                return tp(vs), tp(rs)
            else:
                _curu = _to_unit(ov)
                if valid:
                    res = _curu._process(v)
                    if res.status.valid:
                        return res.result, res
                    else:
                        valid = False
                        return None, res
                else:
                    return None, _curu._skip(v)

        pvalues, rvalues = _recursion(ovalues)
        if valid:
            pres, error = None, None
            try:
                pres = self._transform(v, pvalues)
            except ParseError as err:
                error = err
            except self.__errors__ as err:
                error = err

            if error is None:
                return proxy.success(pres, rvalues)
            else:
                return proxy.error(error, rvalues)
        else:
            return proxy.error(None, rvalues)

    def _rinfo(self):
        return [], [(name, val) for name, val in zip(self.__names__, self._values)]


class CalculateUnit(TransformUnit):
    """
    Overview:
        Simple value calculation unit.
    """

    def _transform(self, v: PValue, pres: Mapping[str, Any]) -> PValue:
        return v.val(self._calculate(
            v.value, nested_map(lambda x: x.value, pres)
        ))

    def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
        """
        Calculation method.

        :param v: Original value.
        :param pres: Pre-processed values.
        :return: Returned value.
        :raises Exception: Raised exception which is instance of ``__errors__`` will be processed.
        """
        raise NotImplementedError  # pragma: no cover
