
LaTeX Expression project documentation
**************************************
.. automodule:: latexexpr

.. toctree::
    :hidden:
    :maxdepth: 3

    index


Classes
=======
The module contains three fundamental classes: :class:`Variable`, :class:`Operation` and :class:`Expression`.

Varibable
---------
.. autoclass:: Variable
	:members:

	.. automethod:: __str__
	.. automethod:: __float__

Operation
---------
.. autoclass:: Operation
	:members:

	.. automethod:: __str__
	.. automethod:: __float__

Expression
----------
.. autoclass:: Expression
	:members:

	.. automethod:: __str__
	.. automethod:: __float__


.. _predefinedOperations:

Predefined Operation instance creation
======================================
Preferable way to create new Operation instances. For each supported operation type there exists corresponding "constructor". All such "constructors" return new Operation instance.

.. autofunction:: SUM
.. autofunction:: ADD
.. autofunction:: PLUS
.. autofunction:: SUB
.. autofunction:: MINUS
.. autofunction:: MUL
.. autofunction:: TIMES
.. autofunction:: DIV
.. autofunction:: DIV2
.. autofunction:: NEG
.. autofunction:: POS
.. autofunction:: ABS
.. autofunction:: MAX
.. autofunction:: MIN
.. autofunction:: POW
.. autofunction:: SQR
.. autofunction:: SQRT
.. autofunction:: SIN
.. autofunction:: COS
.. autofunction:: TAN
.. autofunction:: SINH
.. autofunction:: COSH
.. autofunction:: TANH
.. autofunction:: EXP
.. autofunction:: LOG
.. autofunction:: LN
.. autofunction:: LOG10
.. autofunction:: RBRACKETS
.. autofunction:: BRACKETS
.. autofunction:: SBRACKETS
.. autofunction:: CBRACKETS
.. autofunction:: ABRACKETS


Predefined Variable instances
=============================
Some predefined Variable instances which might be useful in constructing different expressions.

.. autodata:: ONE
.. autodata:: TWO
.. autodata:: E
.. autodata:: PI


Other module members
====================
Some other useful functions and other module members.

.. autoexception:: LaTeXExpressionError
.. autofunction:: saveVars
.. autofunction:: loadVars
.. autofunction:: toLaTeXVariable


Sympy extension
**************************************
.. automodule:: latexexpr.sympy

Sympy functions
====================
.. autofunction:: latexexpr.sympy.simplify
.. autofunction:: latexexpr.sympy.expand
.. autofunction:: latexexpr.sympy.factor
.. autofunction:: latexexpr.sympy.collect
.. autofunction:: latexexpr.sympy.cancel
.. autofunction:: latexexpr.sympy.apart
