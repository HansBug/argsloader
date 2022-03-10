from typing import Mapping, Any, Union, Tuple, List

from hbutils.collection import nested_map
from hbutils.string import truncate

from .base import CalculateUnit, BaseUnit, _to_unit, UnitProcessProxy, TransformUnit
from .utils import keep
from ..base import PValue, ParseResult


class GetItemUnit(TransformUnit):
    __names__ = ('item',)
    __errors__ = (KeyError, IndexError)

    def __init__(self, item, offset: bool = True):
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
            raise type(err)(f'Item {repr(item)} not found.')

    def _rinfo(self):
        _, children = super()._rinfo()
        return [('offset', self._offset)], children


def getitem_(item, offset: bool = True) -> 'GetItemUnit':
    return GetItemUnit(item, not not offset)


class GetAttrUnit(CalculateUnit):
    __names__ = ('attr',)
    __errors__ = (AttributeError,)

    def __init__(self, attr):
        CalculateUnit.__init__(self, attr)

    def _calculate(self, v, pres: Mapping[str, Any]) -> object:
        return getattr(v, pres['attr'])


def getattr_(attr) -> 'GetAttrUnit':
    return GetAttrUnit(attr)


class StructUnit(BaseUnit):
    def __init__(self, struct_):
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


def struct(struct_) -> StructUnit:
    return StructUnit(struct_)


class MappingUnit(BaseUnit):
    def __init__(self, f, offset: bool = True):
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
    return MappingUnit(func, not not offset)


class InUnit(CalculateUnit):
    __names__ = ('instance', 'collection')
    __errors__ = (KeyError, TypeError)

    def __init__(self, instance, collection):
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
    return InUnit(instance, collection)


def isin(collection) -> InUnit:
    return InUnit(keep(), collection)


def contains(instance) -> InUnit:
    return InUnit(instance, keep())
