from typing import Mapping, Any

from hbutils.collection import nested_map

from .base import CalculateUnit, BaseUnit, _to_unit, UnitProcessProxy
from .status import child
from ..base import PValue, ParseResult


class GetItemUnit(CalculateUnit):
    __names__ = ('item',)
    __errors__ = (KeyError, IndexError)

    def __init__(self, item):
        CalculateUnit.__init__(self, item)

    def _calculate(self, v, pres: Mapping[str, Any]) -> object:
        item = pres['item']
        try:
            return v[item]
        except self.__errors__ as err:
            raise type(err)(f'Item {repr(item)} not found.')


def getitem_(item, no_follow: bool = False) -> 'GetItemUnit':
    u = GetItemUnit(item)
    if not no_follow:
        u = u >> child(item)
    return u


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
