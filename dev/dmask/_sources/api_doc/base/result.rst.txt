argsloader.base.result
=================================

.. currentmodule:: argsloader.base.result

.. automodule:: argsloader.base.result


ParseResultChildProxy
-------------------------------

.. autoclass:: ParseResultChildProxy
    :members: __init__, __getitem__, __contains__, keys, items, __hash__, __eq__


ResultStatus
-------------------------------

.. autoenum:: ResultStatus
    :members: valid, processed, loads


ErrMode
-------------------------------

.. autoenum:: ErrMode
    :members: loads


ParseResult
-------------------------------

.. autoclass:: ParseResult
    :members: __init__, __getitem__, __contains__, keys, items, __repr__, input, unit, status, result, error, act


