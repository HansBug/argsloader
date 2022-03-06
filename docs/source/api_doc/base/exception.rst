argsloader.base.exception
=================================

.. currentmodule:: argsloader.base.exception

.. automodule:: argsloader.base.exception


BaseParseError
------------------------

.. autoclass:: BaseParseError
    :members:


ParseError
------------------------

.. autoclass:: ParseError
    :members: __init__, message, unit, value, info, __hash__, __eq__, __repr__


MultipleParseError
------------------------

.. autoclass:: MultipleParseError
    :members: __init__, items, __repr__, __str__


SkippedParseError
------------------------

.. autoclass:: SkippedParseError
    :members: __init__


wrap_exception_class
------------------------------

.. autofunction:: wrap_exception_class


wrap_exception
------------------------------

.. autofunction:: wrap_exception


