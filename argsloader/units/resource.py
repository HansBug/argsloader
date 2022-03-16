import warnings
from enum import unique
from functools import partial
from typing import Mapping, Any, Union

import enum_tools
from hbutils.model import AutoIntEnum
from hbutils.scale import time_to_duration, size_to_bytes

from .build import CalculateUnit


@enum_tools.documentation.document_enum
@unique
class TimeScale(AutoIntEnum):
    """
    Overview:
        Duration unit enum.
    """

    def __init__(self, scale):
        self.scale = scale

    def __repr__(self):
        return f'<{type(self).__name__}.{self.name}: {self.scale}>'

    NANOSECOND = 1e-9  # doc: Nano second, 1 second = 1,000,000,000 nano seconds
    MICROSECOND = 1e-6  # doc: Micro second, 1 second = 1,000,000 micro seconds
    MILLISECOND = 1e-3  # doc: Milli second, 1 second = 1,000 milli seconds
    SECOND = 1.0  # doc: Second, 1 second = 1 second
    MINUTE = 1.0 * 60  # doc: Minute, 1 minute = 60 seconds
    HOUR = 1.0 * 60 * 60  # doc: Hour, 1 hour = 60 * 60 seconds
    DAY = 1.0 * 60 * 60 * 24  # doc: Day, 1 day = 24 * 60 * 60 seconds


class TimespanUnit(CalculateUnit):
    """
    Overview:
        Unit for parsing timespan data.
    """
    __names__ = ()
    __errors__ = (ValueError, TypeError)

    def __init__(self, scale):
        """
        Constructor of :class:`TimespanUnit`.
        
        :param scale: Scale for the result.
        """
        self._scale = scale
        CalculateUnit.__init__(self)

    def _calculate(self, v: Union[float, int, str], pres: Mapping[str, Any]) -> float:
        return time_to_duration(v) / self._scale.scale

    def _rinfo(self):
        _, children = CalculateUnit._rinfo(self)
        return [('unit', self._scale)], children


def timespan():
    """
    Overview:
        Timespan data parsing.

    :return: A timespan parsing unit.

    Examples::
        - Simple usage

        >>> from argsloader.units import timespan
        >>> u = timespan()
        >>> u('5h43min8s')
        20588.0
        >>> u('7day 5minutes ')
        605100.0

        - Get the timespan in minutes

        >>> u = timespan.minutes()
        >>> u('5h43min8s')
        343.1333333333333
        >>> u('7day 5minutes ')
        10085.0

        - Get the timespan in hours

        >>> u = timespan.hours()
        >>> u('5h43min8s')
        5.7188888888888885
        >>> u('7day 5minutes ')
        168.08333333333334

    .. note::

        Supported scales:

        - ``timespan.nano``, which means the parsed result will be in nanoseconds.
        - ``timespan.micro``, which means the parsed result will be in microseconds.
        - ``timespan.milli``, which means the parsed result will be in milliseconds.
        - ``timespan.seconds``, which is the same as simple ``timespan``.
        - ``timespan.minutes``, which means the parsed result will be in minutes.
        - ``timespan.hours``, which means the parsed result will be in hours.
        - ``timespan.days``, which means the parsed result will be in days.
    """
    return TimespanUnit(TimeScale.SECOND)


timespan.nano = partial(TimespanUnit, TimeScale.NANOSECOND)
timespan.micro = partial(TimespanUnit, TimeScale.MICROSECOND)
timespan.milli = partial(TimespanUnit, TimeScale.MILLISECOND)
timespan.seconds = partial(TimespanUnit, TimeScale.SECOND)
timespan.minutes = partial(TimespanUnit, TimeScale.MINUTE)
timespan.hours = partial(TimespanUnit, TimeScale.HOUR)
timespan.days = partial(TimespanUnit, TimeScale.DAY)


@enum_tools.documentation.document_enum
@unique
class MemoryScale(AutoIntEnum):
    """
    Overview:
        Memory size unit enum.
    """

    def __init__(self, scale):
        self.scale = scale

    def __repr__(self):
        return f'<{type(self).__name__}.{self.name}: {self.scale}>'

    B = 1  # doc: Byte, 1 byte = 1 byte.
    KiB = 1 * 1024 ** 1  # doc: KiB, 1 KiB = 1024 bytes.
    KB = 1 * 1000 ** 1  # doc: KB, 1 KB = 1000 bytes.
    MiB = 1 * 1024 ** 2  # doc: MiB, 1 MiB = 1024 * 1024 bytes.
    MB = 1 * 1000 ** 2  # doc: MB, 1 MB = 1000 * 1000 bytes.
    GiB = 1 * 1024 ** 3  # doc: GiB, 1 GiB = 1024 * 1024 * 1024 bytes.
    GB = 1 * 1000 ** 3  # doc: GB, 1 GB = 1000 * 1000 * 1000 bytes.
    TiB = 1 * 1024 ** 4  # doc: TiB, 1 TiB = 1024 * 1024 * 1024 * 1024 bytes.
    TB = 1 * 1000 ** 4  # doc: TB, 1 TB = 1000 * 1000 * 1000 * 1000 bytes.


class MemoryUnit(CalculateUnit):
    """
    Overview:
        Unit for parsing memory size data.
    """
    __names__ = ()
    __errors__ = (ValueError, TypeError)

    def __init__(self, scale: MemoryScale):
        """
        Constructor of :class:`MemoryUnit`.

        :param scale: Scale for the result.
        """
        self._scale = scale
        CalculateUnit.__init__(self)

    def _calculate(self, v: Union[int, float, str], pres: Mapping[str, Any]) -> float:
        with warnings.catch_warnings(record=True):
            bytes_ = size_to_bytes(v)
            if self._scale == MemoryScale.B:
                return bytes_
            else:
                return bytes_ / self._scale.scale

    def _rinfo(self):
        _, children = CalculateUnit._rinfo(self)
        return [('unit', self._scale)], children


def memory_() -> MemoryUnit:
    """
    Overview:
        Memory size data parsing.

    :return: A memory size parsing unit.

    Examples::
        - Simple usage

        >>> from argsloader.units import memory_
        >>> u = memory_()
        >>> u('5M')
        5000000
        >>> u('238.4 Gi')
        255980050842

        - Get the memory in MiB

        >>> u = memory_.MiB()
        >>> u('5M')
        4.76837158203125
        >>> u('238.4 Gi')
        244121.60000038147

        - Get the memory in KB

        >>> u = memory_.KB()
        >>> u('5M')
        5000.0
        >>> u('238.4 Gi')
        255980050.842

    .. note::

        Supported scales:

        - ``memory_.B``, which means the parsed result will be in bytes.
        - ``memory_.bytes``, alias for ``memory_.B``.
        - ``memory_.KiB``, which means the parsed result will be in KiB.
        - ``memory_.KB``, which means the parsed result will be in KB.
        - ``memory_.MiB``, which means the parsed result will be in MiB.
        - ``memory_.MB``, which means the parsed result will be in MB.
        - ``memory_.GiB``, which means the parsed result will be in GiB.
        - ``memory_.GB``, which means the parsed result will be in GB.
        - ``memory_.TiB``, which means the parsed result will be in TiB.
        - ``memory_.TB``, which means the parsed result will be in TB.
    """
    return MemoryUnit(MemoryScale.B)


for key, item in MemoryScale.__members__.items():
    setattr(memory_, key, partial(MemoryUnit, item))

memory_.bytes = memory_.B
