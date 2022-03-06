argsloader.units.base
=================================

.. currentmodule:: argsloader.units.base

.. automodule:: argsloader.units.base


UncompletedUnit
-----------------------

.. autoclass:: UncompletedUnit
    :members: _fail, __call__, call, log, validity


BaseUnit
-----------------------

.. autoclass:: BaseUnit
    :members: __call__, call, log, validity, _process, _skip, _easy_process, __rshift__, __rrshift__, __and__, __rand__, __or__, __ror__


UnitProcessProxy
-----------------------

.. autoclass:: UnitProcessProxy
    :members: __init__, success, error, skipped


ValueUnit
-----------------------

.. autoclass:: ValueUnit
    :members: __init__, _easy_process


raw
-----------------------

.. autofunction:: raw


TransformUnit
-----------------------

.. autoclass:: TransformUnit
    :members: __init__, _transform, _easy_process


CalculateUnit
--------------------------

.. autoclass:: CalculateUnit
    :members: _transform, _calculate

