from typing import Mapping, Any

from hbutils.string import env_template

from .base import _CalculateUnit, _to_unit


class TemplateUnit(_CalculateUnit):
    __names__ = ('tmp', 'vars', 'safe')
    __errors__ = (KeyError,)

    def __init__(self, tmp, variables: Mapping[str, Any], safe):
        _CalculateUnit.__init__(self, tmp, {k: _to_unit(v) for k, v in variables.items()}, safe)

    def _calculate(self, v: object, pres: Mapping[str, Any]) -> object:
        # print(pres)
        return env_template(pres['tmp'], pres['vars'], safe=pres['safe'])


def template(tmp, vars_, safe: bool = False) -> TemplateUnit:
    return TemplateUnit(tmp, vars_, safe)
