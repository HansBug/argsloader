import math
import platform
from enum import Enum, unique
from pprint import pprint

from argsloader.units import cdict, cvalue, number, is_type, ge, enum, timespan, none, yesno


@unique
class RetryType(Enum):
    RESET = 1
    RENEW = 2


@unique
class ContextType(Enum):
    SPAWN = 1
    FORK = 2

    @classmethod
    def default(cls):
        if 'win' in platform.system().lower():
            return cls.SPAWN
        else:
            return cls.FORK


config_loader = cdict(dict(
    episode_num=cvalue(math.inf, number()),  # should be a number
    max_retry=cvalue(5, number() >> is_type(int) >> ge.than(0)),  # should be an int number, >= 0
    step_timeout=cvalue(None, timespan() | none()),  # a timespan or None
    auto_reset=cvalue(True, yesno()),  # is boolean value
    retry_type=cvalue('reset', enum(RetryType)),  # retry type
    reset_timeout=cvalue(None, timespan() | none()),  # a timespan or None
    retry_waiting_time=cvalue(0.1, timespan()),  # a timespan

    # subprocess specified args
    shared_memory=cvalue(True, yesno()),  # should be a yes/no value
    context=cvalue(ContextType.default(), enum(ContextType)),  # context type
    wait_num=cvalue(2, number() >> is_type(int) >> ge.than(0)),  # should be an int number, >=0
    step_wait_timeout=cvalue(0.01, timespan()),  # a timespan in seconds
    connect_timeout=cvalue(60, timespan()),  # a timespan in seconds
    reset_inplace=cvalue(False, yesno()),  # should be a yes/no value
))

if __name__ == '__main__':
    pprint(config_loader.call({
        'connect_timeout': '3h 5min',
        'max_retry': '15',
        'retry_type': 'renew',
        'auto_reset': 'no',
    }), indent=4)
