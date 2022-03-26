from functools import reduce, partial
from operator import __rshift__
from typing import Mapping, Any, Union, Tuple, List

from hbutils.collection import nested_map
from hbutils.design import SingletonMark
from hbutils.string import truncate

from .base import BaseUnit, _to_unit, UnitProcessProxy, raw
from .build import TransformUnit, CalculateUnit, UnitBuilder
from .utils import keep
from ..base import PValue, ParseResult


class GetItemUnit(TransformUnit):
    """
    Overview:
        Unit for getting item from list, tuple or dict object, using ``__getitem__``.
    """
    __names__ = ('item',)
    __errors__ = (KeyError, IndexError)

    def __init__(self, item, offset: bool = True):
        """
        Constructor of :class:`GetItemUnit`.

        :param item: Item data.
        :param offset: Create offset when getting item, default is ``True``.
        """
        self._offset = offset
        TransformUnit.__init__(self, item)

    def _transform(self, v: PValue, pres: Mapping[str, Any]) -> PValue:
        item = pres['item'].value
        try:
            res = v.val(v.value[item])
            if self._offset:
                res = res.child(item)
            return res
        except self.__errors__ as err:
            raise type(err)(f'Item {repr(item)} not found in value.')

    def _rinfo(self):
        _, children = super()._rinfo()
        return [('offset', self._offset)], children


def getitem_(*items, offset: bool = True):
    """
    Overview:
        Getting item from list, tuple and dict, based on ``__getitem__``.

    :param items: Items to be got, units are supported, multiple items are also supported.
    :param offset: Enable offset or not, default is ``True``.
    :return: A unit for getting item.

    Examples::
        - Get item from list and tuple

        >>> from argsloader.units import getitem_
        >>> u = getitem_(2)
        >>> u([2, 3, 5, 7, 11, 13])
        5
        >>> u((2, 3, 5, 7, 11, 13))
        5
        >>> u([2, 3])
        IndexParseError: Item 2 not found in value.

        - Get item from dict

        >>> u = getitem_('b')
        >>> u({'a': 12, 'b': 23})
        23
        >>> u({'b': 24, 'bb': 233})
        24
        >>> u({'a': 12, 'c': 23})
        KeyParseError: "Item 'b' not found in value."

        - Multiple levels

        >>> u = getitem_('a', 2)
        >>> u({'a': [2, 3, 5, 7], 'b': 2})
        5
        >>> u({'a': [2, 3], 'b': 2})
        IndexParseError: Item 2 not found in value.
        >>> u({'aa': [2, 3, 5, 7], 'b': 2})
        KeyParseError: "Item 'a' not found in value."

    .. note::
        When :func:`getitem_` is used, the position of value will be switched to child-level. \
        This can be seen when method :meth:`argsloader.units.base.BaseUnit.call` is called. For example,

        >>> from argsloader.units import getitem_, is_type
        >>> u = getitem_(2) >> is_type(int)
        >>> u.call([2, 3, 5.0])
        argsloader.base.exception.MultipleParseError: (1 error)
          <root>.2: TypeParseError: Value type not match - int expected but float found.
        >>>
        >>> u = getitem_('b') >> is_type(int)
        >>> u.call({'a': 12, 'b': 23.0})
        argsloader.base.exception.MultipleParseError: (1 error)
          <root>.b: TypeParseError: Value type not match - int expected but float found.

        But sometimes this offset should not be kept, so we can disable it. For example, in the following code, \
        This positions of the errors are all ``<root>`` instead of ``<root>.2`` or ``<root>.b``.

        >>> from argsloader.units import getitem_, is_type
        >>> u = getitem_(2, offset=False) >> is_type(int)
        >>> u.call([2, 3, 5.0])
        argsloader.base.exception.MultipleParseError: (1 error)
          <root>: TypeParseError: Value type not match - int expected but float found.
        >>>
        >>> u = getitem_('b', offset=False) >> is_type(int)
        >>> u.call({'a': 12, 'b': 23.0})
        argsloader.base.exception.MultipleParseError: (1 error)
          <root>: TypeParseError: Value type not match - int expected but float found.
    """
    if not items:
        return keep()
    else:
        return reduce(__rshift__, map(partial(GetItemUnit, offset=not not offset), items))


class GetAttrUnit(CalculateUnit):
    """
    Overview:
        Unit for getting attribute from object, using ``__getattr__``.
    """
    __names__ = ('attr',)
    __errors__ = (AttributeError,)

    def __init__(self, attr):
        """
        Constructor of :class:`GetAttrUnit`.

        :param attr: Attribute data.
        """
        CalculateUnit.__init__(self, attr)

    def _calculate(self, v, pres: Mapping[str, Any]) -> object:
        return getattr(v, pres['attr'])


def getattr_(attr) -> 'GetAttrUnit':
    """
    Overview:
        Getting attribute from object, based on ``__getattr__``.

    :param attr: Attribute to be got, units are supported.
    :return: A unit for getting attribute.

    Examples::
        >>> from argsloader.units import getattr_
        >>> from easydict import EasyDict
        >>> u = getattr_('a')
        >>> u(EasyDict({'a': 1, 'b': 2}))
        1
        >>>
        >>> u = getattr_('__dict__')
        >>> u(EasyDict({'a': 1, 'b': 2}))
        {'a': 1, 'b': 2}
    """
    return GetAttrUnit(attr)


class StructUnit(BaseUnit):
    """
    Overview:
        Unit for building structure.
    """

    def __init__(self, struct_):
        """
        Constructor of :class:`StructUnit`.

        :param struct_: Structure data.
        """
        self._struct = nested_map(_to_unit, struct_)

    def _easy_process(self, v: PValue, proxy: UnitProcessProxy) -> ParseResult:
        valid = True

        def _sprocess(u: BaseUnit):
            nonlocal valid
            res = u._process(v)
            if not res.status.valid:
                valid = False
            return res

        records = nested_map(_sprocess, self._struct)
        if valid:
            return proxy.success(v.val(nested_map(lambda r: r.result.value, records)), records)
        else:
            return proxy.error(None, records)

    def _rinfo(self):
        return [], [('struct', self._struct)]


def struct(struct_):
    """
    Overview:
        Quickly build a structure, based on the given ``struct`` data.

    :param struct_: Structure data, which should contain one or multiple units.
    :return: Structed data, which has the same structure with the given ``struct_``.

    Examples::
        >>> u = struct({
        ...     'a': add.by(2) >> interval.LR(1, 15),
        ...     'b': (sub.by(3), 'this is b'),
        ...     'c': [233, mul.by(4)],
        ... })
        >>> u(5)
        {'a': 7, 'b': (2, 'this is b'), 'c': [233, 20]}
        >>> u(10)
        {'a': 12, 'b': (7, 'this is b'), 'c': [233, 40]}
        >>> u(20)
        ValueParseError: Value not in interval - [1, 15] expected but 22 found.

    .. note::
        Extended class of list, tuple or dict's type will be kept. For example,

        >>> from argsloader.units import struct, add, mul, sub, interval
        >>> from easydict import EasyDict
        >>> u = struct({
        ...     'a': add.by(2) >> interval.LR(1, 15),
        ...     'b': (sub.by(3), 'this is b'),
        ...     'c': EasyDict({'x': 233, 'y': mul.by(4)}),
        ... })
        >>> u(5)
        {'a': 7, 'b': (2, 'this is b'), 'c': {'x': 233, 'y': 20}}
        >>> type(u(5))
        <class 'dict'>
        >>> type(u(5)['c'])
        <class 'easydict.EasyDict'>

    .. note::
        Like the ``&`` operator, all the units will be executed, so all the errors will be recorded when \
        method :meth:`argsloader.units.base.BaseUnit.call` is used. For example,

        >>> from argsloader.units import struct, add, mul, sub, interval
        >>> u = struct({
        ...     'a': add.by(2) >> interval.LR(1, 10),
        ...     'b': (sub.by(3) >> interval.LR(0, 5), 'this is b'),
        ...     'c': [233, mul.by(4) >> interval.LR(10, 30)],
        ... })
        >>> u.call(5)
        {'a': 7, 'b': (2, 'this is b'), 'c': [233, 20]}
        >>> u.call(10)
        argsloader.base.exception.MultipleParseError: (3 errors)
          <root>: ValueParseError: Value not in interval - [1, 10] expected but 12 found.
          <root>: ValueParseError: Value not in interval - [0, 5] expected but 7 found.
          <root>: ValueParseError: Value not in interval - [10, 30] expected but 40 found.

    .. warning::
        If the given ``struct_`` is not a dict, list or tuple, the return value will be a simple unit instead of \
        :class:`StructUnit`.
    """
    if isinstance(struct_, (dict, list, tuple)):
        return StructUnit(struct_)
    else:
        return _to_unit(struct_)


class MappingUnit(BaseUnit):
    """
    Overview:
        Unit for processing sequence-based objects.
    """

    def __init__(self, f, offset: bool = True):
        """
        Constructor of :class:`MappingUnit`.

        :param f: Processor function.
        :param offset: Create offset when getting item, default is ``True``.
        """
        self._func = _to_unit(f)
        self._offset = offset

    def _easy_process(self, v: PValue, proxy: UnitProcessProxy) -> ParseResult:
        lst: Union[Tuple, List] = v.value
        valid, records = True, []
        for index, item in enumerate(lst):
            iv = v.val(item)
            if self._offset:
                iv = iv.child(index)

            res = self._func._process(iv)
            valid = valid and res.status.valid
            records.append(res)

        if valid:
            return proxy.success(v.val(type(v.value)(map(lambda x: x.result.value, records))), records)
        else:
            return proxy.error(None, records)

    def _rinfo(self):
        return [], [('func', self._func)]


def mapping(func, offset: bool = True) -> MappingUnit:
    """
    Overview:
        Mapping items from sequence based object.

    :param func: Processor function for mapping.
    :param offset: Enable offset or not, default is ``True``.
    :return: A unit for mapping sequence based-object.

    Examples::
        >>> from argsloader.units import mapping, interval, add
        >>> u = mapping(add.by(2) >> interval.LR(1, 10))
        >>> u([2, 3, 5, 7])
        [4, 5, 7, 9]
        >>> u([2, 3, 5, 71, 11, 13])
        ValueParseError: Value not in interval - [1, 10] expected but 73 found.

    .. note::
        All the values will be processed by the unit, so all the errors will be recorded. For example,

        >>> from argsloader.units import mapping, interval, add
        >>> u = mapping(add.by(2) >> interval.LR(1, 10))
        >>> u.call([2, 3, 5, 7])
        [4, 5, 7, 9]
        >>> u.call([2, 3, 5, 71, 11, 13])
        argsloader.base.exception.MultipleParseError: (3 errors)
          <root>.3: ValueParseError: Value not in interval - [1, 10] expected but 73 found.
          <root>.4: ValueParseError: Value not in interval - [1, 10] expected but 13 found.
          <root>.5: ValueParseError: Value not in interval - [1, 10] expected but 15 found.

    .. note::
        Like function :func:`getitem_`, the position offset is enabled in default. But we can disable it \
        when necessary. For example, in the following code, all the errors will be marked as ``<root>``.

        >>> from argsloader.units import mapping, interval, add
        >>> u = mapping(add.by(2) >> interval.LR(1, 10), offset=False)
        >>> u.call([2, 3, 5, 7])
        [4, 5, 7, 9]
        >>> u.call([2, 3, 5, 71, 11, 13])
        argsloader.base.exception.MultipleParseError: (3 errors)
          <root>: ValueParseError: Value not in interval - [1, 10] expected but 73 found.
          <root>: ValueParseError: Value not in interval - [1, 10] expected but 13 found.
          <root>: ValueParseError: Value not in interval - [1, 10] expected but 15 found.
    """
    return MappingUnit(func, not not offset)


class InUnit(CalculateUnit):
    """
    Overview:
        Unit for checking if one object is **in** another object, using ``__contains__`` method.
    """
    __names__ = ('instance', 'collection')
    __errors__ = (KeyError, TypeError)

    def __init__(self, instance, collection):
        """
        Constructor of :class:`InUnit`.

        :param instance: Instance to be checked.
        :param collection: Collection to be checked.
        """
        CalculateUnit.__init__(self, instance, collection)

    def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
        instance, collection = pres['instance'], pres['collection']
        if instance in collection:
            return v
        else:
            raise KeyError(f'Collection should contain instance, '
                           f'but {repr(instance)} is not included '
                           f'in {truncate(repr(collection))} actually.')


def in_(instance, collection) -> InUnit:
    """
    Overview:
        Containment check, using ``__contains__`` method.

    :param instance: Instance to be checked.
    :param collection: Collection to be checked.
    :return: Unit for checking containment.

    Examples::
        >>> from argsloader.units import in_, add, mul, struct
        >>> u = in_(add.by(2), struct([2, mul.by(2), 5]))
        >>> u(0)  # 2 in [2, 0, 5]
        0
        >>> u(2)  # 4 in [2, 4, 5]
        2
        >>> u(4)  # 6 in [2, 8, 5]
        KeyParseError: 'Collection should contain instance, but 6 is not included in [2, 8, 5] actually.'
    """
    return InUnit(instance, collection)


def isin(collection) -> InUnit:
    """
    Overview:
        Containment check, the same as ``in_(keep(), collection)``.

    :param collection: Collection to be checked.
    :return: Unit for checking containment.

    Examples::
        >>> from argsloader.units import isin, add, mul
        >>> u = add.by(2) >> mul.by(3) >> isin([9, 0, 12])
        >>> u(1)  # 9 in [9, 0, 12]
        9
        >>> u(2)  # 12 in [9, 0, 12]
        12
        >>> u(3)  # 15 in [9, 0, 12]
        KeyParseError: 'Collection should contain instance, but 15 is not included in [9, 0, 12] actually.'
    """
    return in_(keep(), collection)


def contains(instance) -> InUnit:
    """
    Overview:
        Containment check, the same as ``in_(instance, keep())``.

    :param instance: Instance to be checked.
    :return: Unit for checking containment.

    Examples::
        >>> from argsloader.units import contains, add, mul, struct
        >>> u = struct([add.by(2), mul.by(2), 10]) >> contains(8)
        >>> u(4)  # 8 in [6, 8, 10]
        [6, 8, 10]
        >>> u(6)  # 8 in [8, 12, 10]
        [8, 12, 10]
        >>> u(7)  # 8 in [9, 14, 10]
        KeyParseError: 'Collection should contain instance, but 8 is not included in [9, 14, 10] actually.'
    """
    return in_(instance, keep())


UNIT_KEEP = SingletonMark('CVALUE_UNIT_KEEP')
DEFAULT_REQUIRED = SingletonMark('CVALUE_DEFAULT_REQUIRED')


def crequired():
    """
    Overview:
        Get a mark which means this value is required.

        See :func:`cdict`.
    """
    return DEFAULT_REQUIRED


class _CFreeValidation:
    def __init__(self, unit):
        self.unit = _to_unit(unit)


def cfree(unit):
    """
    Overview:
        Processing values freely in :func:`cdict`.
    """
    return _CFreeValidation(unit)


class _CDefaultValidation:
    def __init__(self, ucheck, udefault):
        self.ucheck = ucheck
        self.udefault = udefault


def cvalue(default_, ucheck=UNIT_KEEP) -> _CDefaultValidation:
    """
    Overview:
        Get a value validation mark which means this value item has a default value and some validations.

        See :func:`cdict`.

    :param default_: Default value of this item.
    :param ucheck: Check unit for this item, default means just do not do any validation.

    .. note::
        The validation will be processed after item's getting and default value's applying. \
        This means the given ``default_`` will be processed by ``ucheck`` as well.

    .. warning::
        Do not use unit object in ``default_`` parameter, \
        which will be processed with :func:`argsloader.units.base.raw`. \
        Some unexpected result will be caused due to this misuse.
    """
    ucheck = keep() if ucheck is UNIT_KEEP else _to_unit(ucheck)
    udefault = None if default_ is DEFAULT_REQUIRED else raw(default_)
    return _CDefaultValidation(ucheck, udefault)


class CDictBuilder(UnitBuilder):
    def __init__(self, unit, data):
        UnitBuilder.__init__(self)
        self.__unit = unit
        self.__data = data

    @property
    def data(self):
        return self.__data

    def _build(self) -> BaseUnit:
        return self.__unit


def cdict(dict_: dict):
    """
    Overview:
        Build a :func:`struct` unit to parse dict-based data, with some slight validations.

    :param dict_: Dict-based metadata.
    :return: A :func:`struct` unit.

    Examples::
        - Simple usage

        >>> from argsloader.units import cdict, cvalue, is_type, crequired, add, interval, number
        >>> u = cdict({
        ...     'a': cvalue(1, number()),  # default value with validation
        ...     'b': crequired(),  # required value
        ...     'c': {
        ...         'x': cvalue(4, is_type(int) >> add.by(10)),
        ...         'y': cvalue(crequired(), is_type(int) & interval.LR(0, 10)),
        ...         'z': 5,  # simple default value
        ...     },
        ... })
        >>> u.call({'a': 5, 'b': 10, 'c': {'x': 7, 'y': 9}})
        {'a': 5, 'b': 10, 'c': {'x': 17, 'y': 9, 'z': 5}}
        >>> u.call({'a': '0xff', 'b': -2, 'c': {'y': 4}})
        {'a': 255, 'b': -2, 'c': {'x': 14, 'y': 4, 'z': 5}}
        >>> u.call({'a': '0b101011', 'c': {'x': 6.0, 'y': 100.0}})
        argsloader.base.exception.MultipleParseError: (4 errors)
          <root>: KeyParseError: Item 'b' not found in value.
          <root>.c.x: TypeParseError: Value type not match - int expected but float found.
          <root>.c.y: TypeParseError: Value type not match - int expected but float found.
          <root>.c.y: ValueParseError: Value not in interval - [0, 10] expected but 100.0 found.

        - Keep the original type

        >>> from easydict import EasyDict
        >>> from argsloader.units import cdict, cvalue, number
        >>> u = cdict(EasyDict({
        ...     'a': cvalue(1, number()),
        ...     'b': crequired(),
        ... }))
        >>> u.call({'a': '0xff', 'b': -2})
        {'a': 255, 'b': -2}
        >>> isinstance(u.call({'a': '0xff', 'b': -2}), EasyDict)
        True

        - Nested usage

        >>> from argsloader.units import cdict, cvalue, is_type, crequired, add, interval, number
        >>> u = cdict({
        ...     'a': cvalue(1, number()),
        ...     'b': crequired(),
        ...     'c': cdict({  # inner cdict can be used
        ...         'x': cvalue(4, is_type(int) >> add.by(10)),
        ...         'y': cvalue(crequired(), is_type(int) & interval.LR(0, 10)),
        ...         'z': 5,
        ...     }),
        ... })
        >>> u.call({'a': 5, 'b': 10, 'c': {'x': 7, 'y': 9}})
        {'a': 5, 'b': 10, 'c': {'x': 17, 'y': 9, 'z': 5}}
        >>> u.call({'a': '0xff', 'b': -2, 'c': {'y': 4}})
        {'a': 255, 'b': -2, 'c': {'x': 14, 'y': 4, 'z': 5}}
        >>> u.call({'a': '0b101011', 'c': {'x': 6.0, 'y': 100.0}})
        argsloader.base.exception.MultipleParseError: (4 errors)
          <root>: KeyParseError: Item 'b' not found in value.
          <root>.c.x: TypeParseError: Value type not match - int expected but float found.
          <root>.c.y: TypeParseError: Value type not match - int expected but float found.
          <root>.c.y: ValueParseError: Value not in interval - [0, 10] expected but 100.0 found.

    .. warning::
        Attention that the value items which not appeared in the ``dict_`` value will be ignored. \
        This means the parsing result of function :func:`cdict` will have exactly the same structure \
        as ``dict_``. For example

        >>> from easydict import EasyDict
        >>> from argsloader.units import cdict, cvalue, number
        >>> u = cdict(EasyDict({
        ...     'a': cvalue(1, number()),
        ...     'b': crequired(),
        ... }))
        >>> u.call({'a': '0xff', 'b': -2, 'z': 174})  # z is ignored
        {'a': 255, 'b': -2}

    """

    def _recursion(d, path):
        gitem = reduce(__rshift__, map(getitem_, path)) if path else keep()
        if isinstance(d, _CDefaultValidation):
            if d.udefault is not None:
                return (gitem | d.udefault) >> d.ucheck
            else:
                return gitem >> d.ucheck
        elif isinstance(d, _CFreeValidation):
            ppath = path[:-1]
            pgitem = reduce(__rshift__, map(getitem_, ppath)) if ppath else keep()
            return (pgitem | raw({})) >> d.unit
        elif d is DEFAULT_REQUIRED:
            return gitem
        elif isinstance(d, dict):
            return type(d)({
                key: _recursion(value, (*path, key))
                for key, value in d.items()
            })
        elif isinstance(d, CDictBuilder):
            return _recursion(d.data, path)
        else:
            return gitem | _to_unit(d)

    unit = struct(_recursion(dict_, ()))
    return CDictBuilder(unit, dict_)
