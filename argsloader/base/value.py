from typing import Tuple, Optional

from hbutils.model import asitems, visual, hasheq


@hasheq()
@visual()
@asitems(['value', 'position'])
class PValue:
    def __init__(self, value, position: Optional[Tuple] = None):
        """
        Constructor of class :class:`argsloader.base.value.PValue`.

        :param value: Value of this object.
        :param position: Data position of this object.
        """
        self.__value = value
        self.__position = tuple(position or ())

    @property
    def value(self):
        """
        Value of this project.
        """
        return self.__value

    @property
    def position(self):
        """
        Data position of this project.
        """
        return self.__position

    def child(self, *attach) -> 'PValue':
        """
        Switch position to child level.

        :param attach: Child attachment.
        :return: A new ``PValue`` object.
        """
        return PValue(self.__value, (*self.__position, *attach))

    def parent(self, back=1) -> 'PValue':
        """
        Switch position to parent level.

        :param back: Levels to switch back.
        :return: A new ``PValue`` object.
        """
        return PValue(self.__value, self.__position[:max(len(self.__position) - back, 0)])

    def val(self, value) -> 'PValue':
        """
        Switch value to a new value.

        :param value: New value to be switched.
        :return: A new ``PValue`` object.
        """
        return PValue(value, self.__position)
