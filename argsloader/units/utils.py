from typing import Mapping, Any, List, Tuple

from hbutils.collection import nested_map
from hbutils.design import SingletonMark

from .base import BaseUnit, UnitProcessProxy, _to_unit, UncompletedUnit, _ITreeFormat
from .build import TransformUnit, CalculateUnit
from ..base import PValue, ParseResult, wrap_exception


class KeepUnit(CalculateUnit):
    """
    Overview:
        Unit for keep the original input value.
    """

    def __init__(self):
        """
        Constructor of class :class:`KeepUnit`.
        """
        CalculateUnit.__init__(self)

    def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
        return v


_keep_unit = KeepUnit()


def keep() -> KeepUnit:
    """
    Overview:
        Simply keep the original input data.

        See :class:`KeepUnit`.

    :return: A keep unit object.

    Examples::
        >>> from argsloader.units import keep
        >>> u = keep()
        >>> u(1)
        1
        >>> u('this is str')
        'this is str'
    """
    return _keep_unit


class CheckUnit(CalculateUnit):
    """
    Overview:
        Unit for check, the original input data will be kept.
    """
    __names__ = ('unit',)

    def __init__(self, unit):
        """
        Constructor of :class:`CheckUnit`.

        :param unit: Unit used to check.
        """
        CalculateUnit.__init__(self, unit)

    def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
        return v


def check(unit) -> CheckUnit:
    """
    Overview:
        Simply keep the input data, the ``unit`` is only used for checking.

        See :class:`CheckUnit`.

    :param unit: Unit used to check.
    :return: A check unit object.

    Examples::
        >>> from argsloader.units import check, is_type, add
        >>> u = check(is_type(int) >> add.by(2))
        >>> u(2)
        2
        >>> u(10)
        10
        >>> u(2.0)
        TypeParseError: Value type not match - int expected but float found.
    """
    return CheckUnit(unit)


class ValidityUnit(BaseUnit):
    """
    Overview:
        Unit for getting validity of the given ``unit``.
    """

    def __init__(self, unit: BaseUnit):
        """
        Constructor of :class:`ValidityUnit`.

        :param unit: Unit for getting validity.
        """
        self._unit = _to_unit(unit)

    def _easy_process(self, v: PValue, proxy: UnitProcessProxy) -> ParseResult:
        result: ParseResult = self._unit._process(v)
        return proxy.success(v.val(result.status.valid), {'unit': result})

    def _rinfo(self):
        return [], [('unit', self._unit)]


def validity(unit) -> ValidityUnit:
    """
    Overview:
        Get the validity of the given ``unit``.
        Return ``True`` when ``unit`` is parsed success, otherwise return ``False``.

        See :class:`ValidityUnit`.

    :param unit: Unit for getting validity.
    :return: A validity unit object.

    Examples::
        - Simple usage

        >>> from argsloader.units import validity, is_type
        >>> u = validity(is_type(int))
        >>> u(10)
        True
        >>> u(10.0)
        False

        - Attribute-based usage

        >>> u = is_type(int).validity  # the same as validity(is_type(int))
        >>> u(10)
        True
        >>> u(10.0)
        False
    """
    return ValidityUnit(unit)


class ErrorUnit(TransformUnit):
    """
    Overview:
        Unit for raise errors.
    """
    __names__ = ('condition', 'errcls', 'args')

    def __init__(self, condition, errcls, *args):
        """
        Constructor of :class:`ErrorUnit`.

        :param condition: Condition unit, the error will be raised if condition is satisfied.
        :param errcls: Error class.
        :param args: Error arguments.
        """
        TransformUnit.__init__(self, condition, errcls, args)

    def _transform(self, v: PValue, pres: Mapping[str, Any]) -> PValue:
        condition_ok = pres['condition'].value
        if not condition_ok:
            return v
        else:
            errcls = pres['errcls'].value
            args = tuple(nested_map(lambda x: x.value, pres['args']))
            raise wrap_exception(errcls(*args), self, v)


def error(condition, errcls, *args) -> ErrorUnit:
    """
    Overview:
        Raise error when the given ``condition`` is satisfied.

    :param condition: Condition unit.
    :param errcls: Error class.
    :param args: Error arguments.
    :return: A error unit object.

    Examples::
        >>> from argsloader.units import error, is_type
        >>> u = error(is_type(int).validity, KeyError, 'a key error')
        >>> u(10.0)
        10.0
        >>> u(10)
        KeyParseError: 'a key error'
    """
    return ErrorUnit(condition, errcls, *args)


def validate(val, condition, errcls, *args):
    """
    Overview:
        Raise error based on the validation of data.

    :param val: Data calculation unit.
    :param condition: Validation unit, the error will be raised if this ``condition`` is not satisfied.
    :param errcls: Error class.
    :param args: Error arguments.
    :return: A unit object which can do the validation.

    Examples::
        >>> from argsloader.units import to_type, le, validate
        >>> u = validate(to_type(int), le.than(5).validity, KeyError, 'a key error')
        >>> u(4)
        4
        >>> u(5.2)
        5.2
        >>> u(6.0)
        KeyParseError: 'a key error'
    """
    from .mathop import not_
    return check(_to_unit(val) >> error(not_(_to_unit(condition)), errcls, *args))


def fail(errcls, *args) -> ErrorUnit:
    """
    Overview:
        Raise error at any time.

    :param errcls: Error class.
    :param args: Error arguments.
    :return: A unit object which can raise error.

    Examples::
        >>> from argsloader.units import fail
        >>> u = fail(KeyError, 'a key error')
        >>> u(1)
        KeyParseError: 'a key error'
    """
    return error(True, errcls, *args)


_ELSE_STATEMENT = SingletonMark('ELSE_STATEMENT')


class _IfStatementModel(_ITreeFormat):
    def __init__(self, statements):
        self._statements = statements

    def _rinfo(self):
        children = []
        for i, (_if, _then) in enumerate(self._statements):
            if _if is not _ELSE_STATEMENT:
                if i == 0:
                    children.append(('if', _if))
                    children.append(('then', _then))
                else:
                    children.append((f'elif_{i}', _if))
                    children.append(('then', _then))
            else:
                children.append(('else', _then))

        return [], children


class _IfProxy(_IfStatementModel, UncompletedUnit):
    """
    Overview:
        If proxy object, used to build :class:`IfUnit`.
    """

    def elif_(self, cond, val) -> '_IfProxy':
        """
        Add an ``else-if`` clause.

        :param cond: Condition unit.
        :param val: Value unit.
        :return: Another :class:`_IfProxy` with this new ``else-if`` clause.
        """
        return _IfProxy([*self._statements, (_to_unit(cond), _to_unit(val))])

    def else_(self, val) -> 'IfUnit':
        """
        Add an ``else`` clause.

        :param val: Value unit.
        :return: A completed :class:`IfUnit` with this ``else`` clause.
        """
        return IfUnit([*self._statements, (_ELSE_STATEMENT, _to_unit(val))])

    def _fail(self):
        raise SyntaxError('Uncompleted if statement unit - else statement expected but not found.')


class IfUnit(_IfStatementModel, BaseUnit):
    """
    Overview:
        Unit for if statement.
    """

    def __init__(self, statements: List[Tuple[BaseUnit, BaseUnit]]):
        """
        Constructor of :class:`IfUnit`.

        :param statements: If statements.
        """
        _IfStatementModel.__init__(self, statements)

    def _easy_process(self, v: PValue, proxy: UnitProcessProxy) -> ParseResult:
        completed, valid, result, record = False, True, None, []
        for cond, val in self._statements:
            cond = cond if cond is not _ELSE_STATEMENT else _to_unit(True)
            if not completed:
                cres = cond._process(v)
                if cres.status.valid:
                    if cres.result.value:
                        vres = val._process(v)
                        record.append((cres, vres))
                        if vres.status.valid:
                            completed = True
                            valid = True
                            result = vres.result
                        else:
                            completed = True
                            valid = False
                    else:
                        record.append((cres, val._skip(v)))
                else:
                    completed = True
                    valid = False
                    record.append((cres, val._skip(v)))
            else:
                record.append((cond._skip(v), val._skip(v)))

        if valid:
            return proxy.success(result, record)
        else:
            return proxy.error(None, record)


def if_(cond, val) -> _IfProxy:
    """
    Overview:
        If clause to determine the return value.
    
    :param cond: Condition unit.
    :param val: Value unit.
    :return: An initial :class:`_IfProxy` unit, a full if statement will be built based on this.

    Examples::
        >>> from argsloader.units import if_, is_type
        >>> u = if_(is_type(int).validity, 'an int').elif_(is_type(float).validity, 'a float').else_('fxxk off')
        >>> u(1)
        'an int'
        >>> u(1.0)
        'a float'
        >>> u('1')
        'fxxk off'
    """
    return _IfProxy([(_to_unit(cond), _to_unit(val))])
