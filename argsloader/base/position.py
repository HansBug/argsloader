from abc import ABCMeta, abstractmethod
from typing import Tuple, Union


class BaseDataPosition(metaclass=ABCMeta):
    @abstractmethod
    def represent(self):
        raise NotImplementedError  # pragma: no cover


class PathPosition(BaseDataPosition):
    def __init__(self, init=None):
        self.__init = tuple(init or ())

    def represent(self) -> Tuple[Union[str, int], ...]:
        return self.__init

    def child(self, *attach) -> 'PathPosition':
        return PathPosition((*self.__init, *attach))

    def parent(self, back=1) -> 'PathPosition':
        return PathPosition(self.__init[:len(self.__init) - back])
