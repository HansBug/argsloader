Cheat Sheet of Units
==================================

A cheat sheet will be provided in this part to make \
using the ``argsloader`` easier when you are unsure \
which unit to use.


Types
--------------------

+-------------------------------------------+---------------------------+---------------------------------------+
| What you want to do                       | What you need to write    | Further details                       |
+===========================================+===========================+=======================================+
| check if the given object is              | ``is_type(str)``          | :func:`argsloader.units.type.is_type` |
| a string                                  |                           |                                       |
+-------------------------------------------+---------------------------+                                       |
| check if the given object is a number     | ``is_type((int, float))`` |                                       |
+-------------------------------------------+---------------------------+---------------------------------------+
| transform a given object to string        | ``to_type(str)``          | :func:`argsloader.units.type.to_type` |
+-------------------------------------------+---------------------------+                                       |
| transform a sequence-liked object to list | ``to_type(list)``         |                                       |
+-------------------------------------------+---------------------------+---------------------------------------+



