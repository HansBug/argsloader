from typing import Mapping, Any

from hbutils.collection import nested_map

from .base import TransformUnit
from ..base import PValue


class ChildPositionUnit(TransformUnit):
    __names__ = ('children',)

    def __init__(self, *children):
        TransformUnit.__init__(self, children)

    def _transform(self, v: PValue, pres: Mapping[str, Any]) -> PValue:
        return v.child(*nested_map(lambda x: x.value, pres['children']))


def child(*children) -> ChildPositionUnit:
    return ChildPositionUnit(*children)


class ParentPositionUnit(TransformUnit):
    __names__ = ('level',)

    def __init__(self, level):
        TransformUnit.__init__(self, level)

    def _transform(self, v: PValue, pres: Mapping[str, Any]) -> PValue:
        return v.parent(pres['level'].value)


def parent(level=1) -> ParentPositionUnit:
    return ParentPositionUnit(level)
