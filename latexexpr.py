# coding=utf8
# -*- coding: utf8 -*-
#
#      LaTeX Expression : Python module for easy LaTeX typesetting of algebraic   
#  expressions in symbolic form with automatic substitution and result computation
#                              version 0.2 (2014-03-25)
#  
#                       Copyright (C)  2013-2014  Jan Stransky                       
#  
#             Czech Technical University, Faculty of Civil Engineering,           
#         Department of Structural Mechanics, 166 29 Prague, Czech Republic       
#  
#  LaTeX Expression is free software: you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License as published by the
#  Free Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#  
#  LaTeX Expression is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
#  details.
#  
#  You should have received a copy of the GNU Lesser General Public License along
#  with this program. If not, see <http://www.gnu.org/licenses/>.

r"""
LaTeX Expression is a Python module for easy LaTeX typesetting of algebraic expressions in symbolic form with automatic substitution and result computation,
i.e. of the form var = generalExpression = substitutedExpression = result, e.g.

.. code-block:: none

	r = 3.0 m
	F = 4.0 kN
	M = r*F = 3.0*4.0 = 12 kNm

The expression is based on :class:`.Variable` class, representing physical or mathematical variable (with symbolic name, value and unit). :class:`Expression` has similar meaning, except that instead of value it contains its :class:`Operation`. :class:`Operation` contains its type (all basic operations are implemented, see :ref:`predefinedOperations`) and combine one or more :class:`variable(s) <.Variable>`, :class:`expression(s) <.Expression>` or other :class:`operations <.Operation>`. In this way, the hierarchy of operations may be combined in one :class:`Expression`. Furthermore, where it is reasonable, Python operators are overloaded to make things even more simple and clear.

.. code-block:: python

	>>> v1 = Variable('a_{22}',3.45,'mm') 
	>>> print v1
	a_{22} = 3.45 \ \mathrm{mm}
	>>> v2 = Variable('F',5.876934835,'kN') 
	>>> print v2
	F = 5.88 \ \mathrm{kN}
	>>> v3 = Variable('F',4.34,'kN',exponent=-2) 
	>>> print v3
	F = { 434.00 \cdot 10^{-2} } \ \mathrm{kN}
	>>> v4 = Variable('F',2.564345,'kN',format='%.4f') 
	>>> print v4
	F = 2.5643 \ \mathrm{kN}
	>>> v5 = Variable('F',5.876934835,'kN') 
	>>> print v5
	F = 5.88 \ \mathrm{kN}
	>>> v6 = Variable('F',-6.543,'kN') 
	>>> o1 = (v1 + SQRT(v2)) / (v3 * v4) + v5 
	>>> print o1
	\frac{ {a_{22}} + \sqrt{ {F} } }{ {F} \cdot {F} } + {F} = \frac{ 3.45 + \sqrt{ 5.88 } }{ { 434.00 \cdot 10^{-2} } \cdot 2.5643 } + 5.88
	>>> e1 = Expression('E_1^i',SBRACKETS(o1) - SQR(v6),'kNm') 
	>>> print e1
	E_1^i = \left[ \frac{ {a_{22}} + \sqrt{ {F} } }{ {F} \cdot {F} } + {F} \right] - {F}^2 = \left[ \frac{ 3.45 + \sqrt{ 5.88 } }{ { 434.00 \cdot 10^{-2} } \cdot 2.5643 } + 5.88 \right] - \left( -6.54 \right)^2 = \left(-36.41\right) \ \mathrm{kNm}
	>>> v7 = e1.toVariable() 
	>>> print v7
	E_1^i
	>>> print v7.toLaTeXVariableAll('MYV7')
	\def\MYV7{E_1^i}
	>>> v8 = Variable('F',None,'kN') 
	>>> o4 = v1 + v8 
	>>> e4 = Expression('E_4',o4,'mF') 
	>>> print v8
	F
	>>> print o4
	{a_{22}} + {F} = 3.45 + {F}
	>>> print e4
	E_4 = {a_{22}} + {F} = 3.45 + {F}
	>>> v8.value=2.34 
	>>> print v8
	F = 2.34 \ \mathrm{kN}
	>>> print o4
	{a_{22}} + {F} = 3.45 + 2.34
	>>> print e4
	E_4 = {a_{22}} + {F} = 3.45 + 2.34 = 5.79 \ \mathrm{mF}


The module is distributed under `GNU LGPL license <http://www.gnu.org/licenses/lgpl.html>`_

To see the module "in action", visit `project home page <http://mech.fsv.cvut.cz/~stransky/en/software/latexexpr/>`_.
"""
# some docstrings are not complete (containing %s formatting symbols) and are completed at the end of the script.

import math

version = '0.2'
date = '2014-03-25'
_DEBUG = False


class LaTeXExpressionError(Exception):
	"""Module exception class"""
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return repr(self.msg)


# Auxiliary functions
def _add(self,v):   return ADD(self,v)
def _sub(self,v):   return SUB(self,v)
def _mul(self,v):   return MUL(self,v)
def _div(self,v):   return DIV(self,v)
def _div2(self,v):  return DIV2(self,v)
def _pow(self,v):   return POW(self,v)
def _radd(self,v):  return ADD(v,self)
def _rsub(self,v):  return SUB(v,self)
def _rmul(self,v):  return MUL(v,self)
def _rdiv(self,v):  return DIV(v,self)
def _rdiv2(self,v): return DIV2(v,self)
def _rpow(self,v):  return POW(v,self)
def _neg(self):     return NEG(self)
def _pos(self):     return POS(self)




######################################################################
# Variable class
######################################################################
class Variable(object):
	r"""Class representing mathematical or physical variable, containing information about its symbolic name, value, phyical units and how to format it. It is a fundamental building block of :class:`operations <.Operation>` and :class:`expressions <.Expression>` instances.
	
	This class overloads str() method to return expression "name = value unit" and float() to return numeric result (throws exception if value is None)
	
	This class also overloads +,-,*,/ (division, frac{...}{...} in LaTeX), // (divsion, .../... in LaTeX) and ** (power) operators. They can be used with Variable, Expression or Operation instances resulting into new Operation instance.
	
	:param str name: symbolic name of the variable
	:param float|None value: value of the variable. If value==None, than the Variable is considered as symbolic
	:param str unit: physical unit of the variable
	:param str format: python string to be formatted by the numeric value with '%' operation (e.g. '%e', '%g', '%.4g', '%.3f' etc.). See `Python string formatting docs <http://docs.python.org/2/library/stdtypes.html#string-formatting-operations>`_ for more details.
	:param str unitFormat: python string to be formatted with unit (default is '\mathrm{%s}' for non-italic units inside math mode). For no formatting use '%s'. See `Python string formatting docs <http://docs.python.org/2/library/stdtypes.html#string-formatting-operations>`_ for more details.
	:param int exponent: exponent for scientific representation
	
	.. code-block:: python
	
		>>> v1 = Variable('a_{22}',3.45,'mm') 
		>>> print v1
		a_{22} = 3.45 \ \mathrm{mm}
		>>> v2 = Variable('F',5.876934835,'kN') 
		>>> print v2
		F = 5.88 \ \mathrm{kN}
		>>> v3 = Variable('F',4.34,'kN',exponent=-2) 
		>>> print v3
		F = { 434.00 \cdot 10^{-2} } \ \mathrm{kN}
		>>> v8 = Variable('F',None,'kN') 
		>>> print v8
		F
	"""
	name = ''                   #: symbolic name
	unit = ''                   #: physical unit
	format = '%.2f'             #: string to be formatted by the numeric value (with '%' operation)
	unitFormat = r'\mathrm{%s}' #: string to be formatted by physical unit string (with '%' operation)
	exponent = 0                #: exponent for scientific representation. If 0, then no scientific representation is performed
	def __init__(self,name,value,unit="",format='%.2f',unitFormat=r'\mathrm{%s}',exponent=0):
		self.name = name
		self._value = None if value is None else float(value)
		self.unit = unit
		self.format = format
		self.unitFormat = unitFormat
		self.exponent = exponent
	def _get_value(self):
		return self._value
	def _set_value(self,v):
		self._value = None if v is None else float(v)
	value = property(_get_value,_set_value) #: numeric value. If value==None, than the Variable is considered as symbolic
	def strSymbolic(self):
		"""Returns string of symbolic representation of receiver (its name)
		
		:rtype: str
	
		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> print v1.strSymbolic()
			{a_{22}}
		"""
		return '{%s}'%self.name
	def strSubstituted(self):
		"""Returns string of numeric representation of receiver (its formatted value)
		
		:rtype: str
	
		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> print v1.strSubstituted()
			3.45
		"""
		return self.strResult()
	def strResult(self,format='',exponent=0):
		"""Returns string of the result of the receiver (its formatted result)
		
		:param str format: how to format result if other than predefined in receiver is required
		:param int exponent: exponent the returned string if other than predefined in receiver is required
		:rtype: str
	
		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> print v1.strResult()
			3.45
		"""
		if self.isSymbolic():
			return self.strSymbolic()
		f = format if format else self.format
		e = exponent if exponent!=0 else self.exponent
		result = self.value
		if e==0:
			if result < 0.:
				return r'\left( %s \right)'%f%result
			return '%s'%f%result
		val = self.value*math.pow(10,-e)
		if self.value < 0.:
			return r'\left( %s %s \right)'%(f%val,'\cdot 10^{%d}'%e)
		return '{ %s %s }'%(f%val,'\cdot 10^{%d}'%e)
	def strResultWithUnit(self):
		r"""Returns string of the result of the receiver (its formatted result) ending with its units
		
		:rtype: str
	
		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> print v1.strResultWithUnit()
			3.45 \ \mathrm{mm}
		"""
		return '%s \\ %s'%(self.strResult(),self.unitFormat%self.unit)
	def result(self):
		"""Returns numeric result of the receiver (its value)
		
		:rtype: float
	
		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> print v1.result()
			3.45
		"""
		if self.isSymbolic():
			raise LaTeXExpressionError, "Unknown result of symbolic variable"
		return self.value
	def __float__(self):
		"""Returns numeric result of the receiver
		
		:rtype: float
	
		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> print float(v1)
			3.45
		"""
		return self.result()
	def __str__(self):
		r"""Returns string representation of receiver in the form "name = value unit"
	
		:rtype: str
	
		.. code-block:: python
	
			>>> v3 = Variable('F',4.34,'kN',exponent=-2) 
			>>> print str(v3)
			F = { 434.00 \cdot 10^{-2} } \ \mathrm{kN}
			>>> v8 = Variable('F',None,'kN') 
			>>> print str(v8)
			F
		"""
		if self.isSymbolic():
			return '%s'%(self.name)
		return '%s = %s'%(self.name,self.strResultWithUnit())
	def toLaTeXVariable(self,name,what='float',command='def'):
		r"""Returns latex expression converting receiver to LaTeX variable using \def, \newcommand, or \renewcommand LaTeX command
		
		:param str name: LaTeX name (without initial \\ symbol)
		:param str what: what to include ('float' for numeric value, 'str' for string value (with possible scientific .10^x), 'valunit' for string value + unit , 'all' for str(self)'
		:param str command: LaTeX command to use (without initial \\ symbol) ['def','newcommand','renewcommand']
	
		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> print v1.toLaTeXVariable('AA','float')
			\def\AA{3.45}
			>>> print v1.toLaTeXVariable('AA','str','newcommand')
			\newcommand{\AA}{3.45}
			>>> print v1.toLaTeXVariable('AA','valunit','renewcommand')
			\renewcommand{\AA}{3.45 \ \mathrm{mm}}
			>>> print v1.toLaTeXVariable('AA','all','def')
			\def\AA{a_{22} = 3.45 \ \mathrm{mm}}
		"""
		what = what.lower()
		whats = ('float','str','valunit','all','subst')
		if not what in whats:
			raise LaTeXExpressionError, '%s not in %s'%(what, whats)
		val = self.value if what=='float' else self.strResult() if what=='str' else self.strResultWithUnit() if what=='valunit' else str(self) if what=='all' or what=='subst' else None
		return toLaTeXVariable(name,val,command)
	def toLaTeXVariableFloat(self,name,command='def'):
		"""Shotcut for :meth:`.Variable.toLaTeXVariable` with what='float' """
		return self.toLaTeXVariable(name,what='float',command=command)
	def toLaTeXVariableStr(self,name,command='def'):
		"""Shotcut for :meth:`.Variable.toLaTeXVariable` with what='str' """
		return self.toLaTeXVariable(name,what='str',command=command)
	def toLaTeXVariableValUnit(self,name,command='def'):
		"""Shotcut for :meth:`.Variable.toLaTeXVariable` with what='valunit' """
		return self.toLaTeXVariable(name,what='valunit',command=command)
	def toLaTeXVariableAll(self,name,command='def'):
		"""Shotcut for :meth:`.Variable.toLaTeXVariable` with what='all' """
		return self.toLaTeXVariable(name,what='all',command=command)
	def fromExpression(self,expr):
		"""Copy information from given Expression or Variable. Returns changed receiver
		
		:param Variable|Expression expr: given expression to be copied
		:rtype: Variable"""
		self.name = expr.name
		self.value = None if expr.isSymbolic else float(expr)
		self.unit = expr.unit
		self.format = expr.format
		self.unitFormat = expr.unitFormat
		self.exponent = expr.exponent
		return self
	def copy(self):
		"""Returns hard copy of receiver"""
		ret = Variable()
		ret.name = self.name
		ret.value = self.value
		ret.unit = self.unit
		ret.format = self.format
		ret.unitFormat = self.unitFormat
		ret.exponent = self.exponent
		return ret
	def isSymbolic(self):
		"""Returns if receiver (or at least one of its sub-components) is purely symbolic variable without specific value
		"""
		return self.value is None
Variable.__add__ = _add
Variable.__sub__ = _sub
Variable.__mul__ = _mul
Variable.__div__ = _div
Variable.__floordiv__ = _div2
Variable.__pow__ = _pow
Variable.__radd__ = _radd
Variable.__rsub__ = _rsub
Variable.__rmul__ = _rmul
Variable.__rdiv__ = _rdiv
Variable.__rfloordiv__ = _rdiv2
Variable.__rpow__ = _rpow
Variable.__neg__ = _neg
Variable.__pos__ = _pos
######################################################################








######################################################################
# Operation class
######################################################################
_NONE  = ''
_PLUS  = '+'
_MINUS = '-'
_TIMES = '*'
_DIV   = '/'
_DIV2  = '//'
_NEG   = 'neg'
_POS   = 'pos'
_ABS   = 'abs'
_MAX   = 'max'
_MIN   = 'min'
_POW   = 'pow'
_SQR   = 'sqr'
_ROOT  = 'root'
_SQRT  = 'sqrt'
_SIN   = 'sin'
_COS   = 'cos'
_TAN   = 'tan'
_SINH  = 'sinh'
_COSH  = 'cosh'
_TANH  = 'tanh'
_EXP   = 'exp'
_LOG   = 'log'
_LN    = 'ln'
_LOG10 = 'log10'
_RBRACKETS = '()'
_SBRACKETS = '[]'
_CBRACKETS = '{}'
_ABRACKETS = '<>'

_supportedOperations = (_NONE,_PLUS,_MINUS,_TIMES,_DIV,_DIV2,_NEG,_POS,_ABS,_MAX,_MIN,_POW,_SQR,_ROOT,_SQRT,_SIN,_COS,_TAN,_SINH,_COSH,_TANH,_EXP,_LOG,_LN,_LOG10,_RBRACKETS,_SBRACKETS,_CBRACKETS,_ABRACKETS)
_supportedOperations1 = (_NONE,_NEG,_POS,_ABS,_SQR,_SQRT,_SIN,_COS,_TAN,_SINH,_COSH,_TANH,_EXP,_LN,_LOG10,_RBRACKETS,_SBRACKETS,_CBRACKETS,_ABRACKETS)
_supportedOperations2 = (_MINUS,_DIV,_DIV2,_POW,_ROOT,_LOG)
_supportedOperationsN = (_PLUS,_TIMES,_MAX,_MIN)

class Operation(object):
	r"""Class representing mathematical operation applied to one, two or more objects. These objects may be of type Variable, Expression or Operation again, allowing builing a hieararchy of operations. Preferable way of creation of Operation instances is to use predefined functions (see :ref:`predefinedOperations`) or (where it is possible) standard Python operations +,-,*,/,**.
	
	:param str type: type of operation
	:param Variable(s)|Expression(s)|Operation(s) args: Variables, Expressions, Operations to be combined
	
	.. code-block:: python 
		
		>>> v1 = Variable('a_{22}',3.45,'mm') 
		>>> v2 = Variable('F',5.876934835,'kN') 
		>>> v3 = Variable('F',4.34,'kN',exponent=-2) 
		>>> v4 = Variable('F',2.564345,'kN',format='%.4f') 
		>>> v5 = Variable('F',5.876934835,'kN') 
		>>> v6 = Variable('F',-6.543,'kN') 
		>>> v8 = Variable('F',None,'kN') 
		>>> o3 = (v1+v2)/v3 
		>>> print o3
		\frac{ {a_{22}} + {F} }{ {F} } = \frac{ 3.45 + 5.88 }{ { 434.00 \cdot 10^{-2} } }
		>>> o4 = v1 + v8 
		>>> print o4
		{a_{22}} + {F} = 3.45 + {F}
		>>> e2 = Expression('E_2',(v1+v2)/v3,'mm') 
		>>> o2 = MUL(RBRACKETS(e2+v4),v5,v6) 
		>>> print o2
		\left( {E_2} + {F} \right) \cdot {F} \cdot {F} = \left( 2.15 + 2.5643 \right) \cdot 5.88 \cdot \left( -6.54 \right)
		>>> v8.value=2.34 
		>>> print o4
		{a_{22}} + {F} = 3.45 + 2.34
	"""
	type = None     #: arithmetic type of operation
	args = []       #: arument list subjected to the operation :py:attr:`Operation.type`
	format = '%.2f' # see :py:attr:`Variable.format`
	exponent = 0    # see :py:attr:`Variable.exponent`
	def __init__(self,type,*args):
		if not type in _supportedOperations:
			raise LaTeXExpressionError, 'operation %s not in supported operations %s'%(type,str(_supportedOperations))
		self.type = type
		self.args = self.__checkArgs(args)
		self.format = '%.2f'
		self.exponent = 0
	def __checkArgs(self,args):
		ret = []
		for a in args:
			if isinstance(a,(Variable,Expression,Operation)):
				ret.append(a)
			elif isinstance(a,(float,int)):
				ret.append(Variable('%d'%a,a,format='%d'))
			else:
				raise TypeError, "wrong argunemt type (%s) in Operation constructor"%a.__class__.__name__
		return ret
	def __str(self,what):
		# auxiliary function to format symbolic or substituted expression. Both are the same, the only difference os to call strSymbolic or strSubstituted on receiver args
		a = self.args
		t = self.type
		if t in _supportedOperationsN:
			v = (getattr(arg,what)() for arg in a)
			if t == _PLUS:  return r' + '.join(v)
			if t == _TIMES: return r' \cdot '.join(v)
			if t == _MAX:   return r'\max{\left( %s \right)}'%(', '.join(v))
			if t == _MIN:   return r'\min{\left( %s \right)}'%(', '.join(v))
			if _DEBUG:
				print t
				raise LaTeXExpressionError, t
		if t in _supportedOperations2:
			v0 = getattr(a[0],what)()
			v1 = getattr(a[1],what)()
			if t == _MINUS: return r'%s - %s'%(v0,v1)
			if t == _DIV:   return r'\frac{ %s }{ %s }'%(v0,v1)
			if t == _DIV2:  return r'%s / %s'%(v0,v1)
			if t == _POW:   return r'{ %s }^{ %s }'%(v0,v1)
			if t == _ROOT:  return r'\sqrt[ %s ]{ %s }'%(v0,v1)
			if t == _LOG:   return r'\log_{ %s }{ %s }'%(v0,v1)
			if _DEBUG:
				print t
				raise LaTeXExpressionError, t
		if t in _supportedOperations1:
			v = getattr(a[0],what)()
			if t == _NONE:  return v
			if t == _NEG:   return r'\left( - %s \right)'%v
			if t == _POS:   return v
			if t == _ABS:   return r'\left| %s \right|'%v
			if t == _SQR:   return r'%s^2'%v
			if t == _SQRT:  return r'\sqrt{ %s }'%v
			if t == _SIN:   return r'\sin{ %s }'%v
			if t == _COS:   return r'\cos{ %s }'%v
			if t == _TAN:   return r'\tan{ %s }'%v
			if t == _SINH:  return r'\sinh{ %s }'%v
			if t == _COSH:  return r'\cosh{ %s }'%v
			if t == _TANH:  return r'\tanh{ %s }'%v
			if t == _EXP:   return r'\mathrm{e}^{ %s }'%v
			if t == _LN:    return r'\ln{ %s }'%v
			if t == _LOG10: return r'\log_{10}{ %s }'%v
			if t == _RBRACKETS: return r'\left( %s \right)'%v
			if t == _SBRACKETS: return r'\left[ %s \right]'%v
			if t == _CBRACKETS: return r'\left\{ %s \right\}'%v
			if t == _ABRACKETS: return r'\left\langle %s \right\rangle'%v
			if _DEBUG:
				print t
				raise LaTeXExpressionError, t
		raise LaTeXExpressionError, 'operation %s not in supported operations %s'%(self.type,str(_supportedOperations))
	def strSymbolic(self):
		r"""Returns string of symbolic representation of receiver
		
		:rtype: str
	
		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> v2 = Variable('F',5.876934835,'kN') 
			>>> v3 = Variable('F',4.34,'kN',exponent=-2) 
			>>> o3 = (v1+v2)/v3 
			>>> print o3.strSymbolic()
			\frac{ {a_{22}} + {F} }{ {F} }
		"""
		return self.__str('strSymbolic')
	def strSubstituted(self):
		r"""Returns string of substituted representation of receiver
		
		:rtype: str
	
		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> v2 = Variable('F',5.876934835,'kN') 
			>>> v3 = Variable('F',4.34,'kN',exponent=-2) 
			>>> o3 = (v1+v2)/v3 
			>>> print o3.strSubstituted()
			\frac{ 3.45 + 5.88 }{ { 434.00 \cdot 10^{-2} } }
		"""
		return self.__str('strSubstituted')
	def strResult(self,format='',exponent=0):
		"""Returns string of the result of the receiver (its formatted result)
		
		:param str format: how to format result if other than predefined in receiver is required
		:param int exponent: exponent the returned string if other than predefined in receiver is required
		:rtype: str
	
		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> v2 = Variable('F',5.876934835,'kN') 
			>>> v3 = Variable('F',4.34,'kN',exponent=-2) 
			>>> o3 = (v1+v2)/v3 
			>>> print o3.strResult()
			2.15
		"""
		if self.isSymbolic():
			return self.strSymbolic()
		r = float(self)
		f = format if format else self.format
		e = exponent if exponent!=0 else self.exponent
		if e==0:
			if r < 0.:
				return r'\left( %s \right)'%f%r
			return '%s'%f%r
		val = r*math.pow(10,-e)
		if r < 0.:
			return r'\left( %s %s \right)'%(f%val,'\cdot 10^{%d}'%e)
		return '{ %s %s }'%(f%val,'\cdot 10^{%d}'%e)
	def result(self):
		"""Returns numeric result of the receiver
		
		:rtype: float
	
		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> v2 = Variable('F',5.876934835,'kN') 
			>>> v3 = Variable('F',4.34,'kN',exponent=-2) 
			>>> o3 = (v1+v2)/v3 
			>>> print o3.result()
			2.14906332604
		"""
		a = self.args
		t = self.type
		if t in _supportedOperationsN:
			v = (float(arg) for arg in a)
			if t == _PLUS:  return sum(v)
			if t == _TIMES: return reduce(lambda x,y: x*y, v, 1.)
			if t == _MAX:   return max(v)
			if t == _MIN:   return min(v)
			if _DEBUG:
				print t
				raise LaTeXExpressionError, t
		if t in _supportedOperations2:
			v0 = float(a[0])
			v1 = float(a[1])
			if t == _MINUS: return v0 - v1
			if t == _DIV:   return v0 / v1
			if t == _DIV2:  return v0 / v1
			if t == _POW:   return math.pow(v0,v1)
			if t == _ROOT:  return math.pow(v1,1./v0)
			if t == _LOG:   return log(v1)/log(v0)
			if _DEBUG:
				print t
				raise LaTeXExpressionError, t
		if t in _supportedOperations1:
			v = float(a[0])
			if t == _NONE:  return v
			if t == _NEG:   return -v
			if t == _POS:   return v
			if t == _ABS:   return abs(v)
			if t == _SQR:   return math.pow(v,2)
			if t == _SQRT:  return math.sqrt(v)
			if t == _SIN:   return math.sin(v)
			if t == _COS:   return math.cos(v)
			if t == _TAN:   return math.tan(v)
			if t == _SINH:  return math.sinh(v)
			if t == _COSH:  return math.cosh(v)
			if t == _TANH:  return math.tanh(v)
			if t == _EXP:   return math.exp(v)
			if t == _LN:    return math.log(v)
			if t == _LOG10: return math.log(v)/math.log(10)
			if t == _RBRACKETS: return v
			if t == _SBRACKETS: return v
			if t == _CBRACKETS: return v
			if t == _ABRACKETS: return v
			if _DEBUG:
				print t
				raise LaTeXExpressionError, t
		raise LaTeXExpressionError, 'operation %s not in supported operations %s'%(self.type,str(_supportedOperations))
	def __float__(self):
		"""Returns numeric result of the receiver
		
		:rtype: float
	
		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> v2 = Variable('F',5.876934835,'kN') 
			>>> v3 = Variable('F',4.34,'kN',exponent=-2) 
			>>> o3 = (v1+v2)/v3 
			>>> print float(o3)
			2.14906332604
		"""
		return self.result()
	def __str__(self):
		r"""Returns string representation of receiver in the form "symbolicExpr = substitutedExpr"

		:rtype: str
		
		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> v2 = Variable('F',5.876934835,'kN') 
			>>> v3 = Variable('F',4.34,'kN',exponent=-2) 
			>>> o3 = (v1+v2)/v3 
			>>> print str(o3)
			\frac{ {a_{22}} + {F} }{ {F} } = \frac{ 3.45 + 5.88 }{ { 434.00 \cdot 10^{-2} } }
		"""
		return '%s = %s'%(self.strSymbolic(),self.strSubstituted())
	def toVariable(self,newName='',**kw):
		"""Returns new Variable instance with attributes copied from receiver
	
		:param str newName: new name of returned variable
		:params dict kw: keyword arguments passed to Variable constructor
		:rtype: Variable"""
		return Variable(newName,float(self),**kw)
	def isSymbolic(self):
		"""Returns if receiver (or at least one of its sub-components) is purely symbolic variable without specific value
		"""
		return any(arg.isSymbolic() for arg in self.args)
Operation.__add__ = _add
Operation.__sub__ = _sub
Operation.__mul__ = _mul
Operation.__div__ = _div
Operation.__floordiv__ = _div2
Operation.__pow__ = _pow
Operation.__radd__ = _radd
Operation.__rsub__ = _rsub
Operation.__rmul__ = _rmul
Operation.__rdiv__ = _rdiv
Operation.__rfloordiv__ = _rdiv2
Operation.__rpow__ = _rpow
Operation.__neg__ = _neg
Operation.__pos__ = _pos
Operation.__iadd__ = _add
Operation.__isub__ = _sub
Operation.__imul__ = _mul
Operation.__idiv__ = _div
Operation.__ifloordiv__ = _div2
Operation.__ineg__ = _neg
Operation.__ipos__ = _pos
######################################################################




######################################################################
# Predefined function for Operation instances creation
######################################################################
def SUM(*args):
	"""Returns addition Operation instance
	
	:param Variable(s)|Expression(s)|Operation(s) args: 2 or more objects for summation ( arg0 + arg1 + ... + argLast)"""
	return Operation(_PLUS,*args)
ADD = SUM
"""Alias for :func:`.SUM`"""
PLUS = SUM
"""Alias for :func:`.SUM`"""
def SUB(*args):
	"""Returns subtraction Operation instance
	
	:param Variable(s)|Expression(s)|Operation(s) args: 2 objects for subtraction ( arg0 - arg1)"""
	return Operation(_MINUS,*args)
MINUS = SUB
"""Alias for :func:`.SUB`"""
def MUL(*args):
	"""Returns multiplication Operation instance
	
	:param Variable(s)|Expression(s)|Operation(s) args: 2 or more objects for multiplication ( arg0 * arg1 * ... * argLast )"""
	return Operation(_TIMES,*args)
TIMES = MUL
"""Alias for :func:`.MUL`"""
def DIV(*args):
	"""Returns division Operation instance (in LaTeX marked by \\\\frac{...}{...})
	
	:param Variable(s)|Expression(s)|Operation(s) args: 2 objects for division ( arg0 / arg1)"""
	return Operation(_DIV,*args)
def DIV2(*args):
	"""Returns division Operation instance (in LaTeX marked by .../...
	
	:param Variable(s)|Expression(s)|Operation(s) args: 2 objects for division ( arg0 / arg1)"""
	return Operation(_DIV2,*args)
def NEG(*args):
	"""Returns negation Operation instance
	
	:param Variable|Expression|Operation args: 1 objects for negation ( -arg0)"""
	return Operation(_NEG,*args)
def POS(*args):
	"""Returns the "positivition" (which does nothing actually) Operation instance
	
	:param Variable|Expression|Operation args: 1 object"""
	return Operation(_POS,*args)
def ABS(*args):
	"""Returns absolute value Operation instance
	
	:param Variable(s)|Expression(s)|Operation(s) args: 1 objects for absolute value ( \|arg0\| )"""
	return Operation(_ABS,*args)
def MAX(*args):
	"""Returns max Operation instance
	
	:param Variable(s)|Expression(s)|Operation(s) args: 2 objects for max ( max(arg0,arg1,...,argN) )"""
	return Operation(_MAX,*args)
def MIN(*args):
	"""Returns min Operation instance
	
	:param Variable(s)|Expression(s)|Operation(s) args: 2 objects for min ( min(arg0,arg1,...,argN) )"""
	return Operation(_MIN,*args)
def POW(*args):
	"""Returns power Operation instance
	
	:param Variable(s)|Expression(s)|Operation(s) args: 2 objects for power ( arg0 ^ arg1)"""
	return Operation(_POW,*args)
def SQR(*args):
	"""Returns square Operation instance
	
	:param Variable|Expression|Operation args: 1 objects for square ( arg ^ 2)"""
	return Operation(_SQR,*args)
def ROOT(*args):
	"""Returns root Operation instance
	
	:param Variable|Expression|Operation args: 1 objects for square root ( arg1^(1/arg0) )"""
	return Operation(_ROOT,*args)
def SQRT(*args):
	"""Returns square root Operation instance
	
	:param Variable|Expression|Operation args: 1 objects for square root ( sqrt(arg) )"""
	return Operation(_SQRT,*args)
def SIN(*args):
	"""Returns sinus Operation instance
	
	:param Variable|Expression|Operation args: 1 objects for sinus ( sin(arg) )"""
	return Operation(_SIN,*args)
def COS(*args):
	"""Returns cosinus Operation instance
	
	:param Variable|Expression|Operation args: 1 objects for cosinus ( cos(arg) )"""
	return Operation(_COS,*args)
def TAN(*args):
	"""Returns tangent Operation instance
	
	:param Variable|Expression|Operation args: 1 objects for tangent ( tan(arg) )"""
	return Operation(_TAN,*args)
def SINH(*args):
	"""Returns hyperbolic sinus Operation instance
	
	:param Variable|Expression|Operation args: 1 objects for hyperbolic sinus ( sin(arg) )"""
	return Operation(_SINH,*args)
def COSH(*args):
	"""Returns hyperbolic cosinus Operation instance
	
	:param Variable|Expression|Operation args: 1 objects for hyperbolic cosinus ( cos(arg) )"""
	return Operation(_COSH,*args)
def TANH(*args):
	"""Returns hyperbolic tangent Operation instance
	
	:param Variable|Expression|Operation args: 1 objects for hyperbolic tangent ( tan(arg) )"""
	return Operation(_TANH,*args)
def EXP(*args):
	"""Returns exp Operation instance
	
	:param Variable|Expression|Operation args: 1 objects for exp ( exp(arg)=e^arg )"""
	return Operation(_EXP,*args)
def LOG(*args):
	"""Returns logarithm Operation instance
	
	:param Variable|Expression|Operation args: 2 objects for logarithm ( log_arg0(arg1) = ln(arg1)/ln(arg0) )"""
	return Operation(_EXP,*args)
def LN(*args):
	"""Returns natural logarithm Operation instance
	
	:param Variable|Expression|Operation args: 1 objects for natural logarithm ( ln(arg) )"""
	return Operation(_LN,*args)
def LOG10(*args):
	"""Returns decadic logarithm Operation instance
	
	:param Variable|Expression|Operation args: 1 objects for decadic logarithm ( log_10(arg) )"""
	return Operation(_LOG10,*args)
def RBRACKETS(*args):
	"""Returns round brackets Operation instance (wrapes passed argument to round brackets)
	
	:param Variable|Expression|Operation args: 1 objects for round brackets ( (arg) )"""
	return Operation(_RBRACKETS,*args)
BRACKETS = RBRACKETS
"""Alias for :func:`.RBRACKETS`"""
def SBRACKETS(*args):
	"""Returns square brackets Operation instance (wrapes passed argument to square brackets)
	
	:param Variable|Expression|Operation args: 1 objects for square brackets ( [arg] )"""
	return Operation(_SBRACKETS,*args)
def CBRACKETS(*args):
	"""Returns curly brackets Operation instance (wrapes passed argument to curly brackets)
	
	:param Variable|Expression|Operation args: 1 objects for curly brackets ( {arg} )"""
	return Operation(_CBRACKETS,*args)
def ABRACKETS(*args):
	"""Returns angle brackets Operation instance (wrapes passed argument to angle brackets)
	
	:param Variable|Expression|Operation args: 1 objects for angle brackets ( ⟨arg⟩ )"""
	return Operation(_ABRACKETS,*args)
######################################################################








######################################################################
# Expression class
######################################################################
class Expression(object):
	r"""Class representing mathematical expression 
	
	:param str name: symbolic name of the expression
	:param Operation|Variable|Expression operation: operation of the expression
	:param str unit: physical unit of the expression
	:param str format: python string to be formatted with '%' operation (e.g. '%e', '%g', '%.4g', '%.3f' etc.). See `Python string formatting docs <http://docs.python.org/2/library/stdtypes.html#string-formatting-operations>`_ for more details.
	:param str unitFormat: python string to be formatted with unit (default is '\mathrm{%s}' for non-italic units inside math mode). For no formatting use '%s'. See `Python string formatting docs <http://docs.python.org/2/library/stdtypes.html#string-formatting-operations>`_ for more details.
	:param int exponent: exponent for scientific representation
	
	.. code-block:: python
	
		>>> v1 = Variable('a_{22}',3.45,'mm') 
		>>> v2 = Variable('F',5.876934835,'kN') 
		>>> v3 = Variable('F',4.34,'kN',exponent=-2) 
		>>> v4 = Variable('F',2.564345,'kN',format='%.4f') 
		>>> v5 = Variable('F',5.876934835,'kN') 
		>>> v6 = Variable('F',-6.543,'kN') 
		>>> v8 = Variable('F',None,'kN') 
		>>> o1 = (v1 + SQRT(v2)) / (v3 * v4) + v5 
		>>> e1 = Expression('E_1^i',SBRACKETS(o1) - SQR(v6),'kNm') 
		>>> print e1
		E_1^i = \left[ \frac{ {a_{22}} + \sqrt{ {F} } }{ {F} \cdot {F} } + {F} \right] - {F}^2 = \left[ \frac{ 3.45 + \sqrt{ 5.88 } }{ { 434.00 \cdot 10^{-2} } \cdot 2.5643 } + 5.88 \right] - \left( -6.54 \right)^2 = \left(-36.41\right) \ \mathrm{kNm}
		>>> e2 = Expression('E_2',(v1+v2)/v3,'mm') 
		>>> print e2
		E_2 = \frac{ {a_{22}} + {F} }{ {F} } = \frac{ 3.45 + 5.88 }{ { 434.00 \cdot 10^{-2} } } = 2.15 \ \mathrm{mm}
		>>> o4 = v1 + v8 
		>>> e4 = Expression('E_4',o4,'mF') 
		>>> print e4
		E_4 = {a_{22}} + {F} = 3.45 + {F}
		>>> v8.value=2.34 
		>>> print e4
		E_4 = {a_{22}} + {F} = 3.45 + 2.34 = 5.79 \ \mathrm{mF}
	"""
	name = ""                   #: symbolic name of the expression
	operation = None            #: underlying :class:`.Operation` instance
 	unit = ""                   #: see :py:attr:`Variable.unit`
	format = "%.2f"             #: see :py:attr:`Variable.format`
	unitFormat = r"\mathrm{%s}" #: see :py:attr:`Variable.unitFormat`
	exponent = 0                #: see :py:attr:`Variable.exponent`
	def __init__(self,name,operation,unit="",format='%.2f',unitFormat=r'\mathrm{%s}',exponent=0):
		self.name = name
		self.operation = operation
		self.unit = unit
		self.format = format
		self.unitFormat = unitFormat
		self.exponent = exponent
	def _get_operation(self):
		return self.operation
	def _set_operation(self,o):
		self.operation = o
	o = property(_get_operation,_set_operation) #: Shortcut for :py:meth:`operation <Expression.operation>`
	def strSymbolic(self):
		"""Returns string of symbolic representation of receiver (its name)
		
		:rtype: str
	
		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> v2 = Variable('F',5.876934835,'kN') 
			>>> v3 = Variable('F',4.34,'kN',exponent=-2) 
			>>> e2 = Expression('E_2',(v1+v2)/v3,'mm') 
			>>> print e2.strSymbolic()
			{E_2}
		"""
		return '{%s}'%self.name
	def strSubstituted(self):
		"""Returns string of numeric representation of receiver (its formatted result)
		
		:rtype: str
	
		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> v2 = Variable('F',5.876934835,'kN') 
			>>> v3 = Variable('F',4.34,'kN',exponent=-2) 
			>>> e2 = Expression('E_2',(v1+v2)/v3,'mm') 
			>>> print e2.strSubstituted()
			2.15
		"""
		return self.strResult()
	def strResult(self,format='',exponent=0):
		"""Returns string of the result of the receiver (its formatted result)
		
		:param str format: how to format result if other than predefined in receiver is required
		:param int exponent: exponent the returned string if other than predefined in receiver is required
		:rtype: str
	
		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> v2 = Variable('F',5.876934835,'kN') 
			>>> v3 = Variable('F',4.34,'kN',exponent=-2) 
			>>> e2 = Expression('E_2',(v1+v2)/v3,'mm') 
			>>> print e2.strResult()
			2.15
		"""
		if self.isSymbolic():
			return self.operation.strSubstituted()
		r = float(self)
		f = format if format else self.format
		e = exponent if exponent!=0 else self.exponent
		if e==0:
			if r < 0:
				return r'\left(%s\right)'%f%r
			return '%s'%f%r
		val = float(self)*math.pow(10,-e)
		if r < 0:
			return r'\left( %s %s \right)'%(f%val,'\cdot 10^{%d}'%e)
		return '{ %s %s }'%(f%val,'\cdot 10^{%d}'%e)
	def strResultWithUnit(self):
		r"""Returns string of the result of the receiver (its formatted result) ending with its units
		
		:rtype: str
	
		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> v2 = Variable('F',5.876934835,'kN') 
			>>> v3 = Variable('F',4.34,'kN',exponent=-2) 
			>>> e2 = Expression('E_2',(v1+v2)/v3,'mm') 
			>>> print e2.strResultWithUnit()
			2.15 \ \mathrm{mm}
		"""
		return '%s \\ %s'%(self.strResult(),self.unitFormat%self.unit)
	def result(self):
		"""Returns numeric result of the receiver
		
		:rtype: float
	
		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> v2 = Variable('F',5.876934835,'kN') 
			>>> v3 = Variable('F',4.34,'kN',exponent=-2) 
			>>> e2 = Expression('E_2',(v1+v2)/v3,'mm') 
			>>> print e2.result()
			2.14906332604
		"""
		return float(self.operation)
	def __float__(self):
		"""Returns numeric result of the receiver
		
		:rtype: float
	
		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> v2 = Variable('F',5.876934835,'kN') 
			>>> v3 = Variable('F',4.34,'kN',exponent=-2) 
			>>> e2 = Expression('E_2',(v1+v2)/v3,'mm') 
			>>> print float(e2)
			2.14906332604
		"""
		return self.result()
	def toVariable(self,newName=''):
		"""Returns new Variable instance with attributes copied from receiver
	
		:param str newName: optional new name of returned variable
		:rtype: Variable"""
		ret = Variable('',0,'').fromExpression(self)
		if newName:
			ret.name = newName
		return ret
	def __str__(self):
		r"""Returns string representation of receiver in the form "name = symbolicExpr = substitutedExpr = result unit"
		
		:rtype: str

		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> v2 = Variable('F',5.876934835,'kN') 
			>>> v3 = Variable('F',4.34,'kN',exponent=-2) 
			>>> e2 = Expression('E_2',(v1+v2)/v3,'mm') 
			>>> print str(e2)
			E_2 = \frac{ {a_{22}} + {F} }{ {F} } = \frac{ 3.45 + 5.88 }{ { 434.00 \cdot 10^{-2} } } = 2.15 \ \mathrm{mm}
		"""
		if self.isSymbolic():
			return '%s = %s'%(self.name,self.operation)
		return '%s = %s = %s'%(self.name,self.operation,self.strResultWithUnit())
	def toLaTeXVariable(self,name,what='float',command='def'):
		r"""Returns latex expression converting receiver to LaTeX variable using \def, \newcommand, or \renewcommand LaTeX command
		
		:param str name: LaTeX name (without initial \\ symbol)
		:param str what: what to include ('float' for numeric value, 'str' for string value (with possible scientific .10^x), 'valunit' for string value + unit , 'symb' for symbolic expression, 'subst' for substrituted expression and 'all' for str(self)'
		:param str command: LaTeX command to use (without initial \\ symbol) ['def','newcommand','renewcommand']
	
		.. code-block:: python
	
			>>> v1 = Variable('a_{22}',3.45,'mm') 
			>>> v2 = Variable('F',5.876934835,'kN') 
			>>> v3 = Variable('F',4.34,'kN',exponent=-2) 
			>>> e2 = Expression('E_2',(v1+v2)/v3,'mm') 
			>>> print e2.toLaTeXVariable('ETWO','float')
			\def\ETWO{2.14906332604}
			>>> print e2.toLaTeXVariable('ETWO','str','newcommand')
			\newcommand{\ETWO}{2.15}
			>>> print e2.toLaTeXVariable('ETWO','valunit','renewcommand')
			\renewcommand{\ETWO}{2.15 \ \mathrm{mm}}
			>>> print e2.toLaTeXVariable('ETWO','symb')
			\def\ETWO{{E_2}}
			>>> print e2.toLaTeXVariable('ETWO','subst')
			\def\ETWO{2.15}
			>>> print e2.toLaTeXVariable('ETWO','all','def')
			\def\ETWO{E_2 = \frac{ {a_{22}} + {F} }{ {F} } = \frac{ 3.45 + 5.88 }{ { 434.00 \cdot 10^{-2} } } = 2.15 \ \mathrm{mm}}
		"""
		what = what.lower()
		whats = ('float','str','valunit','symb','subst','all')
		if not what in whats:
			raise LaTeXExpressionError, '%s not in %s'%(what, whats)
		val = float(self) if what=='float' else self.strResult() if what=='str' else self.strResultWithUnit() if what=='valunit' else self.strSymbolic() if what=='symb' else self.strSubstituted() if what=='subst' else str(self) if what=='all' else None
		return toLaTeXVariable(name,val,command)
	def toLaTeXVariableFloat(self,name,command='def'):
		"""Shotcut for :meth:`.Variable.toLaTeXVariable` with what='float' """
		return self.toLaTeXVariable(name,what='float',command=command)
	def toLaTeXVariableStr(self,name,command='def'):
		"""Shotcut for :meth:`.Variable.toLaTeXVariable` with what='str' """
		return self.toLaTeXVariable(name,what='str',command=command)
	def toLaTeXVariableValUnit(self,name,command='def'):
		"""Shotcut for :meth:`.Variable.toLaTeXVariable` with what='valunit' """
		return self.toLaTeXVariable(name,what='valunit',command=command)
	def toLaTeXVariableSymb(self,name,command='def'):
		"""Shotcut for :meth:`.Variable.toLaTeXVariable` with what='symb' """
		return self.toLaTeXVariable(name,what='symb',command=command)
	def toLaTeXVariableSubst(self,name,command='def'):
		"""Shotcut for :meth:`.Variable.toLaTeXVariable` with what='subst' """
		return self.toLaTeXVariable(name,what='subst',command=command)
	def toLaTeXVariableAll(self,name,command='def'):
		"""Shotcut for :meth:`.Variable.toLaTeXVariable` with what='all' """
		return self.toLaTeXVariable(name,what='all',command=command)
	def isSymbolic(self):
		"""Returns if receiver (or at least one of its sub-components) is purely symbolic variable without specific value
		"""
		return self.operation.isSymbolic()
Expression.__add__ = _add
Expression.__sub__ = _sub
Expression.__mul__ = _mul
Expression.__div__ = _div
Expression.__floordiv__ = _div2
Expression.__pow__ = _pow
Expression.__radd__ = _radd
Expression.__rsub__ = _rsub
Expression.__rmul__ = _rmul
Expression.__rdiv__ = _rdiv
Expression.__rfloordiv__ = _rdiv2
Expression.__rpow__ = _rpow
Expression.__neg__ = _neg
Expression.__pos__ = _pos
######################################################################







######################################################################
# Predefined variable instances
######################################################################
ZERO = Variable('0',0.,format='%d')
"""Variable instance representing 1"""
ONE = Variable('1',1.,format='%d')
"""Variable instance representing 1"""
TWO = Variable('2',2.,format='%d')
"""Variable instance representing 2"""
E   = Variable('\mathrm{e}',math.e)
"""Variable instance representing Euler number"""
PI  = Variable('\pi',math.pi)
"""Variable instance representing pi"""
######################################################################










######################################################################
# other functions
######################################################################
def saveVars(what,fileName='/tmp/latexexprglobals.out'):
	"""Saves globally defined variables from current session into a file. This simplifies working within one LaTeX document, but several python sessions
	
	:param dict what: dictionary object (like locals() or globals()) to be saved
	:param string fileName: name of file to save the variables
	"""
	# http://stackoverflow.com/questions/2960864/how-can-i-save-all-the-variables-in-the-current-python-session
	import shelve
	my_shelf = shelve.open(fileName,'n') # 'n' for new
	for key in what:
		if key.startswith('__') and key.endswith('__'):
			continue
		try:
			my_shelf[key] = what[key]
		except (TypeError,KeyError):
			pass # __builtins__, my_shelf, and imported modules can not be shelved.
	my_shelf.close()

def loadVars(what,fileName='/tmp/latexexprglobals.out'):
	"""Loads saved variables form a file into global namespace
	
	:param dict what: dictionary object (like locals() or globals()) that will be updated with laded values
	:param string fileName: name of file with saved variables
	"""
	# http://stackoverflow.com/questions/2960864/how-can-i-save-all-the-variables-in-the-current-python-session
	import shelve
	my_shelf = shelve.open(fileName)
	for key in my_shelf:
		what[key] = my_shelf[key]
	my_shelf.close()


def toLaTeXVariable(name,what,command='def'):
	r"""Returns latex expression converting receiver to LaTeX variable using \def, \newcommand, or \renewcommand LaTeX command
	
	:param str name: LaTeX name (without initial \\ symbol)
	:param str what: string of the variable body
	:param str command: LaTeX command to use (without initial \\ symbol) ['def','newcommand','renewcommand']
	
	.. code-block:: python
	
			>>> n,s = 'varName','some string content of the variable' 
			>>> print toLaTeXVariable(n,s)
			\def\varName{some string content of the variable}
			>>> print toLaTeXVariable(n,s,'newcommand')
			\newcommand{\varName}{some string content of the variable}
			>>> print toLaTeXVariable(n,s,'renewcommand')
			\renewcommand{\varName}{some string content of the variable}
	"""
	if command == 'def':
		return r'\def\%s{%s}'%(name,what)
	elif command == 'newcommand' or command == 'renewcommand':
		return r'\%s{\%s}{%s}'%(command,name,what)
	else:
		raise LaTeXExpressionError, "toLaTeXVariable: wrong command parameter (should be in ['def','newcommand','renewcommand']"
######################################################################




# TESTING
if __name__ == "__main__":

	v1 = Variable('a_{22}',3.45,'mm')
	print v1
	v2 = Variable('F',5.876934835,'kN')
	print v2
	v3 = Variable('F',4.34,'kN',exponent=-2)
	print v3
	v4 = Variable('F',2.564345,'kN',format='%.4f')
	print v4
	v5 = Variable('F',5.876934835,'kN')
	print v5
	v6 = Variable('F',-6.543,'kN')
	o1 = (v1 + SQRT(v2)) / (v3 * v4) + v5
	print o1
	e1 = Expression('E_1^i',SBRACKETS(o1) - SQR(v6),'kNm')
	print e1
	v7 = e1.toVariable()
	print v7
	print v7.toLaTeXVariableAll('MYV7')
	v8 = Variable('F',None,'kN')
	o4 = v1 + v8
	e4 = Expression('E_4',o4,'mF')
	print v8
	print o4
	print e4
	v8.value=2.34
	print v8
	print o4
	print e4

	v1 = Variable('a_{22}',3.45,'mm')
	print v1
	v2 = Variable('F',5.876934835,'kN')
	print v2
	v3 = Variable('F',4.34,'kN',exponent=-2)
	print v3
	v8 = Variable('F',None,'kN')
	print v8

	v3 = Variable('F',4.34,'kN',exponent=-2)
	print str(v3)
	v8 = Variable('F',None,'kN')
	print str(v8)

	v1 = Variable('a_{22}',3.45,'mm')
	print v1.strSymbolic()

	v1 = Variable('a_{22}',3.45,'mm')
	print v1.strSubstituted()

	v1 = Variable('a_{22}',3.45,'mm')
	print v1.strResult()

	v1 = Variable('a_{22}',3.45,'mm')
	print v1.strResultWithUnit()

	v1 = Variable('a_{22}',3.45,'mm')
	print v1.result()

	v1 = Variable('a_{22}',3.45,'mm')
	print float(v1)

	v1 = Variable('a_{22}',3.45,'mm')
	print v1.toLaTeXVariable('AA','float')
	print v1.toLaTeXVariable('AA','str','newcommand')
	print v1.toLaTeXVariable('AA','valunit','renewcommand')
	print v1.toLaTeXVariable('AA','all','def')

	v1 = Variable('a_{22}',3.45,'mm')
	v2 = Variable('F',5.876934835,'kN')
	v3 = Variable('F',4.34,'kN',exponent=-2)
	v4 = Variable('F',2.564345,'kN',format='%.4f')
	v5 = Variable('F',5.876934835,'kN')
	v6 = Variable('F',-6.543,'kN')
	v8 = Variable('F',None,'kN')
	o3 = (v1+v2)/v3
	print o3
	o4 = v1 + v8
	print o4
	e2 = Expression('E_2',(v1+v2)/v3,'mm')
	o2 = MUL(RBRACKETS(e2+v4),v5,v6)
	print o2
	v8.value=2.34
	print o4

	v1 = Variable('a_{22}',3.45,'mm')
	v2 = Variable('F',5.876934835,'kN')
	v3 = Variable('F',4.34,'kN',exponent=-2)
	o3 = (v1+v2)/v3
	print str(o3)

	v1 = Variable('a_{22}',3.45,'mm')
	v2 = Variable('F',5.876934835,'kN')
	v3 = Variable('F',4.34,'kN',exponent=-2)
	o3 = (v1+v2)/v3
	print o3.strSymbolic()

	v1 = Variable('a_{22}',3.45,'mm')
	v2 = Variable('F',5.876934835,'kN')
	v3 = Variable('F',4.34,'kN',exponent=-2)
	o3 = (v1+v2)/v3
	print o3.strSubstituted()

	v1 = Variable('a_{22}',3.45,'mm')
	v2 = Variable('F',5.876934835,'kN')
	v3 = Variable('F',4.34,'kN',exponent=-2)
	o3 = (v1+v2)/v3
	print o3.strResult()

	v1 = Variable('a_{22}',3.45,'mm')
	v2 = Variable('F',5.876934835,'kN')
	v3 = Variable('F',4.34,'kN',exponent=-2)
	o3 = (v1+v2)/v3
	print o3.result()

	v1 = Variable('a_{22}',3.45,'mm')
	v2 = Variable('F',5.876934835,'kN')
	v3 = Variable('F',4.34,'kN',exponent=-2)
	o3 = (v1+v2)/v3
	print float(o3)

	v1 = Variable('a_{22}',3.45,'mm')
	v2 = Variable('F',5.876934835,'kN')
	v3 = Variable('F',4.34,'kN',exponent=-2)
	v4 = Variable('F',2.564345,'kN',format='%.4f')
	v5 = Variable('F',5.876934835,'kN')
	v6 = Variable('F',-6.543,'kN')
	v8 = Variable('F',None,'kN')
	o1 = (v1 + SQRT(v2)) / (v3 * v4) + v5
	e1 = Expression('E_1^i',SBRACKETS(o1) - SQR(v6),'kNm')
	print e1
	e2 = Expression('E_2',(v1+v2)/v3,'mm')
	print e2
	o4 = v1 + v8
	e4 = Expression('E_4',o4,'mF')
	print e4
	v8.value=2.34
	print e4

	v1 = Variable('a_{22}',3.45,'mm')
	v2 = Variable('F',5.876934835,'kN')
	v3 = Variable('F',4.34,'kN',exponent=-2)
	e2 = Expression('E_2',(v1+v2)/v3,'mm')
	print str(e2)

	v1 = Variable('a_{22}',3.45,'mm')
	v2 = Variable('F',5.876934835,'kN')
	v3 = Variable('F',4.34,'kN',exponent=-2)
	e2 = Expression('E_2',(v1+v2)/v3,'mm')
	print e2.strSymbolic()

	v1 = Variable('a_{22}',3.45,'mm')
	v2 = Variable('F',5.876934835,'kN')
	v3 = Variable('F',4.34,'kN',exponent=-2)
	e2 = Expression('E_2',(v1+v2)/v3,'mm')
	print e2.strSubstituted()

	v1 = Variable('a_{22}',3.45,'mm')
	v2 = Variable('F',5.876934835,'kN')
	v3 = Variable('F',4.34,'kN',exponent=-2)
	e2 = Expression('E_2',(v1+v2)/v3,'mm')
	print e2.strResult()

	v1 = Variable('a_{22}',3.45,'mm')
	v2 = Variable('F',5.876934835,'kN')
	v3 = Variable('F',4.34,'kN',exponent=-2)
	e2 = Expression('E_2',(v1+v2)/v3,'mm')
	print e2.strResultWithUnit()

	v1 = Variable('a_{22}',3.45,'mm')
	v2 = Variable('F',5.876934835,'kN')
	v3 = Variable('F',4.34,'kN',exponent=-2)
	e2 = Expression('E_2',(v1+v2)/v3,'mm')
	print e2.result()

	v1 = Variable('a_{22}',3.45,'mm')
	v2 = Variable('F',5.876934835,'kN')
	v3 = Variable('F',4.34,'kN',exponent=-2)
	e2 = Expression('E_2',(v1+v2)/v3,'mm')
	print float(e2)

	v1 = Variable('a_{22}',3.45,'mm')
	v2 = Variable('F',5.876934835,'kN')
	v3 = Variable('F',4.34,'kN',exponent=-2)
	e2 = Expression('E_2',(v1+v2)/v3,'mm')
	print e2.toLaTeXVariable('ETWO','float')
	print e2.toLaTeXVariable('ETWO','str','newcommand')
	print e2.toLaTeXVariable('ETWO','valunit','renewcommand')
	print e2.toLaTeXVariable('ETWO','symb')
	print e2.toLaTeXVariable('ETWO','subst')
	print e2.toLaTeXVariable('ETWO','all','def')

	n,s = 'varName','some string content of the variable'
	print toLaTeXVariable(n,s)
	print toLaTeXVariable(n,s,'newcommand')
	print toLaTeXVariable(n,s,'renewcommand')
######################################################################
