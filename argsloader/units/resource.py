from enum import unique
from typing import Mapping, Any

from hbutils.model import AutoIntEnum, int_enum_loads
from hbutils.scale import time_to_duration

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
        CalculateUnit.__init__(self, )

    def _calculate(self, v, pres: Mapping[str, Any]) -> float:
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
