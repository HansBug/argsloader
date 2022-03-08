from enum import unique
from typing import Mapping, Any, Union

from hbutils.model import AutoIntEnum, int_enum_loads
from hbutils.scale import time_to_duration, size_to_bytes

from .base import CalculateUnit


@int_enum_loads(name_preprocess=str.upper)
@unique
class TimeScale(AutoIntEnum):
    def __init__(self, scale):
        self.scale = scale

    def __repr__(self):
        return f'<{type(self).__name__}.{self.name}: {self.scale}>'

    NANOSECOND = 1e-9
    MICROSECOND = 1e-6
    MILLISECOND = 1e-3
    SECOND = 1.0
    MINUTE = 1.0 * 60
    HOUR = 1.0 * 60 * 60
    DAY = 1.0 * 60 * 60 * 24


class TimespanUnit(CalculateUnit):
    __names__ = ()
    __errors__ = (ValueError, TypeError)

    def __init__(self, unit):
        self._unit = TimeScale.loads(unit)
        CalculateUnit.__init__(self)

    def _calculate(self, v: Union[float, int, str], pres: Mapping[str, Any]) -> float:
        return time_to_duration(v) / self._unit.scale

    def _rinfo(self):
        _, children = CalculateUnit._rinfo(self)
        return [('unit', self._unit)], children

    @property
    def nano(self):
        return self.__class__('nanosecond')

    @property
    def micro(self):
        return self.__class__('microsecond')

    @property
    def milli(self):
        return self.__class__('millisecond')

    @property
    def seconds(self):
        return self.__class__('second')

    @property
    def minutes(self):
        return self.__class__('minute')

    @property
    def hours(self):
        return self.__class__('hour')

    @property
    def days(self):
        return self.__class__('day')


timespan = TimespanUnit(TimeScale.SECOND)


@unique
class MemoryScale(AutoIntEnum):
    def __init__(self, scale):
        self.scale = scale

    def __repr__(self):
        return f'<{type(self).__name__}.{self.name}: {self.scale}>'

    B = 1.0
    KiB = 1.0 * 1024 ** 1
    KB = 1.0 * 1000 ** 1
    MiB = 1.0 * 1024 ** 2
    MB = 1.0 * 1000 ** 2
    GiB = 1.0 * 1024 ** 3
    GB = 1.0 * 1000 ** 3
    TiB = 1.0 * 1024 ** 4
    TB = 1.0 * 1000 ** 4


class MemoryUnit(CalculateUnit):
    __names__ = ()
    __errors__ = (ValueError, TypeError)

    def __init__(self, unit: MemoryScale):
        self._unit = unit
        CalculateUnit.__init__(self)

    def _calculate(self, v: Union[int, float, str], pres: Mapping[str, Any]) -> float:
        return size_to_bytes(v) / self._unit.scale

    def _rinfo(self):
        _, children = CalculateUnit._rinfo(self)
        return [('unit', self._unit)], children

    @property
    def bytes(self):
        return self.__class__(MemoryScale.B)

    # noinspection PyPep8Naming
    @property
    def KiB(self):
        return self.__class__(MemoryScale.KiB)

    # noinspection PyPep8Naming
    @property
    def KB(self):
        return self.__class__(MemoryScale.KB)

    # noinspection PyPep8Naming
    @property
    def MiB(self):
        return self.__class__(MemoryScale.MiB)

    # noinspection PyPep8Naming
    @property
    def MB(self):
        return self.__class__(MemoryScale.MB)

    # noinspection PyPep8Naming
    @property
    def GiB(self):
        return self.__class__(MemoryScale.GiB)

    # noinspection PyPep8Naming
    @property
    def GB(self):
        return self.__class__(MemoryScale.GB)

    # noinspection PyPep8Naming
    @property
    def TiB(self):
        return self.__class__(MemoryScale.TiB)

    # noinspection PyPep8Naming
    @property
    def TB(self):
        return self.__class__(MemoryScale.TB)


memory_ = MemoryUnit(MemoryScale.B)
