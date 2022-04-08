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


Math Calculation
----------------------

.. todo::
    Complete this part, such as add, sub, etc.


Math Validation
------------------------

.. list-table:: Unit Usage About Math Validation
    :widths: 50 30 20
    :header-rows: 1

    *   - What you want to do
        - What you need to write
        - Further details

    *   - Check if the given value is less than or equal to ``2``
        - .. code-block::

            le.than(2)

        - - :ref:`argsloader-units-mathop-le`

    *   - Check if the given value is less than ``2``
        - .. code-block::

            lt.than(2)

        - - :ref:`argsloader-units-mathop-lt`

    *   - Check if the given value is greater than or equal to ``2``
        - .. code-block::

            ge.than(2)

        - - :ref:`argsloader-units-mathop-ge`

    *   - Check if the given value is greater than ``2``
        - .. code-block::

            gt.than(2)

        - - :ref:`argsloader-units-mathop-gt`

    *   - Check if the given value is equal to ``2``
        - .. code-block::

            eq.to_(2)

        - - :ref:`argsloader-units-mathop-eq`

    *   - Check if the given value is not equal to ``2``
        - .. code-block::

            ne.to_(2)

        - - :ref:`argsloader-units-mathop-ne`

    *   - Check if ``x + 2`` is greater than or equal to ``x ** 2`` (assume the given value is ``x``)
        - .. code-block::

            ge(add.by(2), mul.by(2))

        - - :ref:`argsloader-units-mathop-ge`
          - :ref:`argsloader-units-mathop-add`
          - :ref:`argsloader-units-mathop-mul`

    *   - Check if ``x + 2`` is equal to ``x * 2`` (assume the given value is ``x``)
        - .. code-block::

            eq(add.by(2), mul.by(2))

        - - :ref:`argsloader-units-mathop-eq`
          - :ref:`argsloader-units-mathop-add`
          - :ref:`argsloader-units-mathop-mul`




Numeric Validation
------------------------

.. list-table:: Unit Usage About Numeric Validation
    :widths: 50 30 20
    :header-rows: 1

    *   - What you want to do
        - What you need to write
        - Further details

    *   - Check if the given value is a number (float, int or number-liked str), and then transform it to a number
        - .. code-block::

            number()

        - - :ref:`argsloader-units-numeric-number`

    *   - Check if the given value falls within the interval ``(x, y)``
        - .. code-block::

            interval.lr(x, y)

        - - :ref:`argsloader-units-numeric-interval`


    *   - Check if the given value falls within the interval ``(x, y]``
        - .. code-block::

            interval.lR(x, y)

        - - :ref:`argsloader-units-numeric-interval`

    *   - Check if the given value falls within the interval ``[x, y)``
        - .. code-block::

            interval.Lr(x, y)

        - - :ref:`argsloader-units-numeric-interval`

    *   - Check if the given value falls within the interval ``[x, y]``
        - .. code-block::

            interval.LR(x, y)

        - - :ref:`argsloader-units-numeric-interval`

    *   - Check if the given value falls within the interval ``[x, +inf]``
        - .. code-block::

            interval.L(x)

        - - :ref:`argsloader-units-numeric-interval`

    *   - Check if the given value falls within the interval ``(x, +inf]``
        - .. code-block::

            interval.l(x)

        - - :ref:`argsloader-units-numeric-interval`

    *   - Check if the given value falls within the interval ``[-inf, y]``
        - .. code-block::

            interval.R(y)

        - - :ref:`argsloader-units-numeric-interval`

    *   - Check if the given value falls within the interval ``[-inf, y)``
        - .. code-block::

            interval.r(y)

        - - :ref:`argsloader-units-numeric-interval`

    *   - Check if the given value falls within the interval ``[-inf, y1] | (x2, y2]``
        - .. code-block::

            interval.R(y1).lR(x2, y2)

        - - :ref:`argsloader-units-numeric-interval`



Compound Condition
-------------------------------

.. list-table:: Unit Usage About Compound Condition
    :widths: 50 30 20
    :header-rows: 1

    *   - What you want to do
        - What you need to write
        - Further details

    *   - Check if the given value is an integer which is greater than or equal to ``2``
        - .. code-block::

            is_type(int) & ge.than(2)

        - - :ref:`argsloader-units-type-is_type`
          - :ref:`argsloader-units-mathop-ge`
          - :ref:`argsloader-units-operator-_cand`

    *   - Check if the given value is a string or an value which is greater than or equal to ``2``
        - .. code-block::

            is_type(str) | ge.than(2)

        - - :ref:`argsloader-units-type-is_type`
          - :ref:`argsloader-units-mathop-ge`
          - :ref:`argsloader-units-operator-_cor`

    *   - Calculate the ``2 ** x``, and then check if it falls within interval ``[10, 100)``
        - .. code-block::

            pow_.by(2) >> interval.Lr(10, 100)

        - - :ref:`argsloader-units-mathop-pow_`
          - :ref:`argsloader-units-numeric-interval`
          - :ref:`argsloader-units-operator-_cpipe`


String or Text
-----------------------------

.. list-table:: Unit Usage About String or Text
    :widths: 50 30 20
    :header-rows: 1

    *   - What you want to do
        - What you need to write
        - Further details

    *   - Get the prefixed 11-digits phone number if it is
        - .. code-block::

            regexp('\\d{11}').match

        - - :ref:`argsloader-units-string-regexp`

    *   - Get this 11-digits phone number if it is
        - .. code-block::

            regexp('\\d{11}').match.full

        - - :ref:`argsloader-units-string-regexp`

    *   - Check if the prefix of the given text is a 11-digits phone number (similar with ``re.match``)
        - .. code-block::

            regexp('\\d{11}').match.check

        - - :ref:`argsloader-units-string-regexp`

    *   - Check if the given text is a 11-digits phone number (similar with ``re.fullmatch``)
        - .. code-block::

            regexp('\\d{11}').match.full.check

        - - :ref:`argsloader-units-string-regexp`

    *   - Get the NIN(from 1st to 3rd letter) of the 11-digits phone number
        - .. code-block::

            regexp('(\\d{3})(\\d{4})(\\d{4})').match[0]

        - - :ref:`argsloader-units-string-regexp`

    *   - Get the NIN(1st - 3rd), HLR(4th - 7th) and personal number (8th - 11th) of the 11-digits phone number with a triple tuple
        - .. code-block::

            regexp('(\\d{3})(\\d{4})(\\d{4})').match[(1, 2, 3)]

        - - :ref:`argsloader-units-string-regexp`

