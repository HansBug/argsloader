Cheat Sheet of Units
==================================

A cheat sheet will be provided in this part to make \
using the ``argsloader`` easier when you are unsure \
which unit to use.


Types
--------------------

.. list-table:: Unit Usage About Types
    :widths: 50 30 20
    :header-rows: 1

    *   - What you want to do
        - What you need to write
        - Further details

    *   - Check if the given object is a string
        - .. code-block:: python

            is_type(str)

        - - :ref:`argsloader-units-type-is_type`

    *   - Check if the given object is a list or tuple
        - .. code-block::

            is_type((list, tuple))

        - - :ref:`argsloader-units-type-is_type`

    *   - Transform a given object to string
        - .. code-block::

            to_type(str)

        - - :ref:`argsloader-units-type-to_type`

    *   - Transform a sequence-liked object to list
        - .. code-block::

            to_type(list)

        - - :ref:`argsloader-units-type-to_type`

    *   - Check if the given class is a subclass of dict
        - .. code-block::

            is_subclass(dict)

        - - :ref:`argsloader-units-type-is_subclass`



Data Structure
--------------------

.. list-table:: Unit Usage About Data Structures
    :widths: 50 30 20
    :header-rows: 1

    *   - What you want to do
        - What you need to write
        - Further details

    *   - Get item ``a`` from the given dict object
        - .. code-block::

            getitem_('a')

        - - :ref:`argsloader-units-structure-getitem_`

    *   - Get 2nd item from the given list or tuple
        - .. code-block::

            getitem_(1)

        - - :ref:`argsloader-units-structure-getitem_`

    *   - Get item ``a`` from the given dict object, which is not the original data and position offset should be disabled
        - .. code-block::

            getitem_('a', offset=False)

        - - :ref:`argsloader-units-structure-getitem_`

    *   - Get attribute ``__dict__`` from the given object
        - .. code-block::

            getattr_('__dict__')

        - - :ref:`argsloader-units-structure-getattr_`

    *   - Get value of ``a`` from ``EasyDict``, based on getter of attribute
        - .. code-block::

            getattr_('a')

        - - :ref:`argsloader-units-structure-getattr_`

    *   - Create a tuple which contains ``x + 2`` and ``x`` (assume the given value is ``x``)
        - .. code-block::

            struct((add.by(2), keep))

        - - :ref:`argsloader-units-structure-struct`
          - :ref:`argsloader-units-mathop-add`
          - :ref:`argsloader-units-utils-keep`

    *   - Create a dict with ``x + 2`` and ``x`` (assume the given value is ``x``)
        - .. code-block::

            struct({
                'plus2': add.by(2),
                'origin': keep(),
            })

        - - :ref:`argsloader-units-structure-struct`
          - :ref:`argsloader-units-mathop-add`
          - :ref:`argsloader-units-utils-keep`

    *   - Create nested structure, like ``{'plus': (X, X), 'origin': X}``
        - .. code-block::

            struct({
                'plus': (
                    add.by(2),
                    add.by(4),
                ),
                'origin': keep(),
            })

        - - :ref:`argsloader-units-structure-struct`
          - :ref:`argsloader-units-mathop-add`
          - :ref:`argsloader-units-utils-keep`

