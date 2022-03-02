from typing import Tuple, Optional

from hbutils.model import asitems, visual, hasheq


@hasheq()
@visual()
@asitems(['value', 'position'])
class PValue:
    def __init__(self, value, position: Optional[Tuple] = None):
        self.__value = value
        self.__position = tuple(position or ())

    @property
    def value(self):
        return self.__value

    @property
    def position(self):
        return self.__position

    def child(self, *attach) -> 'PValue':
        return PValue(self.__value, (*self.__position, *attach))

    def parent(self, back=1) -> 'PValue':
        return PValue(self.__value, self.__position[:max(len(self.__position) - back, 0)])

    def val(self, value) -> 'PValue':
        return PValue(value, self.__position)
