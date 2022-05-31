# coding=utf8
# -*- coding: utf8 -*-
#
#      LaTeX Expression : Python module for easy LaTeX typesetting of algebraic   
#  expressions in symbolic form with automatic substitution and result computation
#                            version 0.4.dev (2015-03-03)
#  
#                       Copyright (C)  2013-2015  Jan Stransky                       
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

r"""latexexpr.sympy is an extension for LaTeXExpression for symbolic operations (specifically :func:`.simplify`, :func:`.expand`, :func:`factor`, :func:`collect`, :func:`cancel`, :func:`apart` functions). It requires `sympy <http://www.sympy.org>`_ module. Most of the examples in this documentation is borrowed from `sympy documentation <http://docs.sympy.org/dev/tutorial/simplification.html>`_.

If `sympy <http://www.sympy.org>`_ is present, it also defines aforementioned methods on :class:`Expression <latexexpr.Expression>` and :class:`Operation <latexexpr.Operation>` classes, so it is possible to use both :func:`.simplify` and o.simplify():

.. code-block:: python

	>>> import latexexpr.sympy as lsympy 
	>>> v1 = latexexpr.Variable('v1',None) 
	>>> v2 = latexexpr.Variable('v2',None) 
	>>> v3 = latexexpr.Variable('v3',1.23) 
	>>> v4 = latexexpr.Variable('v4',4.56) 
	>>> x = latexexpr.Variable('x',None) 
	>>> e1 = latexexpr.Expression('e1',v1+v1+v2+v3+v2+v3-v4) 
	>>> print e1
	e1 = {v1} + {v1} + {v2} + {v3} + {v2} + {v3} - {v4}
	>>> print lsympy.simplify(e1)
	e1 = \left( - {v4} \right) + {2} \cdot {v1} + {2} \cdot {v2} + {2} \cdot {v3}
	>>> print lsympy.simplify(e1,substituteFloats=True)
	e1 = {-2.1} + {2} \cdot {v1} + {2} \cdot {v2}
	>>> e1.simplify() 
	>>> print e1
	e1 = \left( - {v4} \right) + {2} \cdot {v1} + {2} \cdot {v2} + {2} \cdot {v3}
	>>> e1.simplify(substituteFloats=True) 
	>>> print e1
	e1 = {-2.1} + {2} \cdot {v1} + {2} \cdot {v2}
	>>> e2 = latexexpr.Expression('e2',latexexpr.SIN(x)**2+latexexpr.COS(x)**2) 
	>>> print lsympy.simplify(e2)
	e2 = 1 = 1 \ \mathrm{} = 1 \ \mathrm{}
	>>> e3 = latexexpr.Expression('e3', (x**3 + x**2 - x - 1) / (x**2 + 2*x + 1) ) 
	>>> print lsympy.simplify(e3)
	e3 = {-1} + {x}
"""

import copy
import latexexpr
try:
	import sympy
except ImportError:
	raise ImportError, "module 'sympy' is not available, therefore latexexpr.sympy will not be available"


def _operation2sympy(arg,varMap=None,substituteFloats=True):
	sf = substituteFloats
	if varMap is None:
		varMap = {}
	if isinstance(arg,latexexpr.Variable):
		if not arg.isSymbolic() and arg.name == '%g'%arg.value:
			if arg.value == int(arg.value):
				return int(arg), varMap
			return float(arg), varMap
		if not sf or arg.isSymbolic():
			varMap[arg.name] = arg
			return sympy.Symbol(arg.name), varMap
		return float(arg), varMap
	if isinstance(arg,latexexpr.Expression):
		return _operation2sympy(arg.operation,varMap,sf)
	if not isinstance(arg,latexexpr.Operation):
		raise TypeError, "TODO " + str(type(arg)) + str(arg)
	t = arg.type
	if t in latexexpr._supportedOperationsN:
		if   t == latexexpr._ADD: sympyOp = sympy.Add
		elif t == latexexpr._MUL: sympyOp = sympy.Mul
		#elif t == latexexpr._MAX: sympyOp = sympy.add.Add # TODO
		#elif t == latexexpr._MIN: sympyOp = sympy.add.Add # TODO
		args = [_o2s(a,varMap,sf) for a in arg.args]
		return sympyOp(*args), varMap
	if t in latexexpr._supportedOperations2:
		a = arg.args
		if t == latexexpr._SUB:
			sympyOp,args = sympy.Add, (_o2s(a[0],varMap,sf),sympy.Mul(-1,_o2s(a[1],varMap,sf)))
		elif t == latexexpr._DIV or t == latexexpr._DIV2:
			sympyOp,args =  sympy.Mul, (_o2s(a[0],varMap,sf),sympy.power.Pow(_o2s(a[1],varMap,sf),-1))
		elif t == latexexpr._POW:   
			sympyOp,args = sympy.Pow, (_o2s(a[0],varMap,sf),_o2s(a[1],varMap,sf))
		elif t == latexexpr._ROOT:  
			sympyOp,args = sympy.Pow, (_o2s(a[0],varMap,sf),_o2s(-a[1],varMap,sf))
		elif t == latexexpr._LOG:
			sympyOp,args = sympy.log, (_o2s(a[0],varMap,sf),_o2s(a[1],varMap,sf))
		return sympyOp(*args), varMap
	if t in latexexpr._supportedOperations1:
		a = arg.args[0]
		if t == latexexpr._NEG:
			sympyOp,args = sympy.Mul, (_o2s(a,varMap,sf),-1)
		elif t == latexexpr._ABS:
			sympyOp,args = sympy.Abs, None
		elif t == latexexpr._SQR:
			sympyOp,args = sympy.Pow, (_o2s(a,varMap,sf),2)
		elif t == latexexpr._SQRT:
			sympyOp,args = sympy.Pow, (_o2s(a,varMap,sf),-2)
		elif t == latexexpr._SIN:
			sympyOp,args = sympy.sin, None
		elif t == latexexpr._COS:
			sympyOp,args = sympy.cos, None
		elif t == latexexpr._TAN:
			sympyOp,args = sympy.tan, None
		elif t == latexexpr._SINH:
			sympyOp,args = sympy.sinh, None
		elif t == latexexpr._COSH:
			sympyOp,args = sympy.sinh, None
		elif t == latexexpr._TANH:
			sympyOp,args = sympy.sinh, None
		elif t == latexexpr._EXP:
			sympyOp,args = sympy.exp, None
		elif t == latexexpr._LN:
			sympyOp,args = sympy.log, None
		elif t == latexexpr._LOG10:
			sympyOp,args = sympy.log, (a,10) # TODO check formula
		elif t in (latexexpr._NONE,latexexpr._RBRACKETS,latexexpr._SBRACKETS,latexexpr._CBRACKETS,latexexpr._ABRACKETS,latexexpr._POS):
			return _operation2sympy(a,varMap,sf)
		if args is None:
			args = (_o2s(a,varMap,sf),)
		return sympyOp(*args), varMap
	raise latexexpr.LaTeXExpressionError, "TODO"
def _o2s(arg,varMap,substituteFloats):
	return _operation2sympy(arg,varMap,substituteFloats)[0]

def _sympy2operation(sympyExpr,varMap):
	if sympyExpr.is_Float or sympyExpr.is_Integer:
		if isinstance(sympyExpr,sympy.numbers.Exp1):
			name = 'e'
		elif isinstance(sympyExpr,sympy.numbers.Pi):
			name = r'\pi'
		# TODO?
		else:
			name = '%g'%float(sympyExpr)
		return latexexpr.Variable(name,float(sympyExpr))
	#
	if isinstance(sympyExpr,sympy.Symbol):
		return varMap[sympyExpr.name]
	args = [_s2o(a,varMap) for a in sympyExpr.args]
	if isinstance(sympyExpr,sympy.Add):
		if len(args)==2 and isinstance(args[1],latexexpr.Operation) and args[1].type==latexexpr._NEG:
			args[1] = args[1].args[0]
			return latexexpr.SUB(*args)
		return latexexpr.ADD(*args)
	if isinstance(sympyExpr,sympy.Mul):
		if len(args)==2:
			if isinstance(args[0],latexexpr.Variable) and args[0].name == '-1':
				return -args[1]
			if isinstance(args[1],latexexpr.Variable) and args[1].name == '-1':
				return -args[0]
		elif len(args)==2 and isinstance(args[1],latexexpr.Operation) and args[1].type==latexexpr._DIV:
			if args[1].args[0].value==1.:
				return args[0] / args[1].args[1]
			if all(a.type==latexexpr._LN for a in (args[0],args[1].args[0])):
				return latexexpr._LOG(args[0],args[0].args[1])
		for i,a in enumerate(args):
			t = a.type if isinstance(a,latexexpr.Operation) else a.operation.type if isinstance(a,latexexpr.Expression) else None
			if t in (latexexpr._ADD,latexexpr._SUB): # TODO?
				args[i] = latexexpr.BRACKETS(a)
		return latexexpr.MUL(*args)
	if isinstance(sympyExpr,sympy.Pow):
		if len(args)==2:
			n = args[1].name if isinstance(args[1],latexexpr.Variable) else None
			if n == '-1':
				return 1. / args[0]
			if n == '2':
				return args[0] ** 2
			if n == '0.5':
				return latexexpr._SQRT(args[1])
		# TODO arg ^ int?
		a = args[0]
		t = a.type if isinstance(a,latexexpr.Operation) else a.operation.type if isinstance(a,latexexpr.Expression) else None
		if t in (latexexpr._ADD,latexexpr._SUB): # TODO?
			args[0] = latexexpr.BRACKETS(a)
		return args[0] ** args[1]
	for s,l in (
			(sympy.Abs,latexexpr.ABS),
			(sympy.sin,latexexpr.SIN),
			(sympy.cos,latexexpr.COS),
			(sympy.tan,latexexpr.TAN),
			(sympy.sinh,latexexpr.SINH),
			(sympy.cosh,latexexpr.COSH),
			(sympy.tanh,latexexpr.TANH),
			(sympy.tanh,latexexpr.TANH),
			(sympy.log,latexexpr.LN),
		):
		if isinstance(sympyExpr,s):
			return l(args[0])
	if isinstance(sympyExpr,sympy.Rational):
		p,q = sympyExpr.p,sympyExpr.q
		if p > 0:
			return latexexpr.Variable(str(p),p) / latexexpr.Variable(str(q),q)
		p = -p
		return - ( latexexpr.Variable(str(p),p) / latexexpr.Variable(str(q),q) )
	#
	# TODO
	raise latexexpr.LaTeXExpressionError, "TODO"
_s2o = _sympy2operation

def simplify(arg,substituteFloats=False,**kw):
	r"""Performs simplify operation on arg. Symbolic variables are left symbolic, but variables with values are treated as the values (!)
	
	:param Variable|Operation|Expression arg: argument to be processed
	:param bool substituteFloats: non-symbolic variables are treated as their float values if True, they are left otherwise
	:param \*\*kw: keywords for sympy.simplify() function
	:rtype: type(arg)
	
	.. code-block:: python
	
		>>> import latexexpr.sympy as lsympy 
		>>> v1 = latexexpr.Variable('v1',None) 
		>>> v2 = latexexpr.Variable('v2',None) 
		>>> v3 = latexexpr.Variable('v3',1.23) 
		>>> v4 = latexexpr.Variable('v4',4.56) 
		>>> x = latexexpr.Variable('x',None) 
		>>> e1 = latexexpr.Expression('e1',v1+v1+v2+v3+v2+v3-v4) 
		>>> print e1
		e1 = {v1} + {v1} + {v2} + {v3} + {v2} + {v3} - {v4}
		>>> print lsympy.simplify(e1)
		e1 = \left( - {v4} \right) + {2} \cdot {v1} + {2} \cdot {v2} + {2} \cdot {v3}
		>>> print lsympy.simplify(e1,substituteFloats=True)
		e1 = {-2.1} + {2} \cdot {v1} + {2} \cdot {v2}
		>>> e1.simplify() 
		>>> print e1
		e1 = \left( - {v4} \right) + {2} \cdot {v1} + {2} \cdot {v2} + {2} \cdot {v3}
		>>> e1.simplify(substituteFloats=True) 
		>>> print e1
		e1 = {-2.1} + {2} \cdot {v1} + {2} \cdot {v2}
		>>> e2 = latexexpr.Expression('e2',latexexpr.SIN(x)**2+latexexpr.COS(x)**2) 
		>>> print lsympy.simplify(e2)
		e2 = 1 = 1 \ \mathrm{} = 1 \ \mathrm{}
		>>> e3 = latexexpr.Expression('e3', (x**3 + x**2 - x - 1) / (x**2 + 2*x + 1) ) 
		>>> print lsympy.simplify(e3)
		e3 = {-1} + {x}
	"""
	if isinstance(arg,latexexpr.Variable):
		return arg
	if isinstance(arg,latexexpr.Expression):
		ret = copy.copy(arg)
		ret.simplify(substituteFloats,**kw)
		return ret
	if isinstance(arg,latexexpr.Operation):
		s,lVars = _operation2sympy(arg,substituteFloats=substituteFloats)
		s = sympy.simplify(s,**kw)
		return _sympy2operation(s,lVars)
	raise TypeError, "Unsupported type (%s) for simplify"%(arg.__class__.__name__)

latexexpr.Expression.simplify = lambda self,substituteFloats=False,**kw: _setOperation(self,simplify(self.operation,substituteFloats=substituteFloats,**kw))

latexexpr.Operation.simplify = lambda self,substituteFloats=False,**kw: _copyOperation(self,simplify(self,substituteFloats=substituteFloats,**kw))

def expand(arg,substituteFloats=False,**kw):
	r"""Performs expand operation on arg. Symbolic variables are left symbolic, but variables with values are treated as the values (!)
	
	:param Variable|Operation|Expression arg: argument to be processed
	:param bool substituteFloats: non-symbolic variables are treated as their float values if True, they are left otherwise
	:param \*\*kw: keywords for sympy.expand() function
	:rtype: type(arg)
	
	.. code-block:: python
	
		>>> import latexexpr.sympy as lsympy 
		>>> x = latexexpr.Variable('x',None) 
		>>> e1 = latexexpr.Expression('e1', (x+1)**2 ) 
		>>> print lsympy.expand(e1,substituteFloats=True)
		e1 = {1} + {2} \cdot {x} + { {x} }^{ {2} }
		>>> e2 = latexexpr.Expression('e2', (x+2)*(x-3) ) 
		>>> print lsympy.expand(e2)
		e2 = {-6} + \left( - {x} \right) + { {x} }^{ {2} }
		>>> e3 = latexexpr.Expression('e3', (x+1)*(x-2) - (x-1)*x ) 
		>>> print lsympy.expand(e3)
		e3 = -2 = \left( -2 \right) \ \mathrm{} = \left(-2\right) \ \mathrm{}
	"""
	if isinstance(arg,latexexpr.Variable):
		return arg
	if isinstance(arg,latexexpr.Expression):
		ret = copy.copy(arg)
		ret.expand(substituteFloats,**kw)
		return ret
	if isinstance(arg,latexexpr.Operation):
		s,lVars = _operation2sympy(arg,substituteFloats=substituteFloats)
		s = sympy.expand(s,**kw)
		return _sympy2operation(s,lVars)
	raise TypeError, "Unsupported type (%s) for expand"%(arg.__class__.__name__)

latexexpr.Expression.expand = lambda self,substituteFloats=False,**kw: _setOperation(self,expand(self.operation,substituteFloats=substituteFloats,**kw))

latexexpr.Operation.expand = lambda self,substituteFloats=False,**kw: _copyOperation(self,expand(self,substituteFloats=substituteFloats,**kw))

def factor(arg,substituteFloats=False,**kw):
	r"""Performs factor operation on arg. Symbolic variables are left symbolic, but variables with values are treated as the values (!)
	
	:param Variable|Operation|Expression arg: argument to be processed
	:param bool substituteFloats: non-symbolic variables are treated as their float values if True, they are left otherwise
	:param \*\*kw: keywords for sympy.factor() function
	:rtype: type(arg)
	
	.. code-block:: python
	
		>>> import latexexpr.sympy as lsympy 
		>>> x = latexexpr.Variable('x',None) 
		>>> y = latexexpr.Variable('y',None) 
		>>> z = latexexpr.Variable('z',None) 
		>>> e1 = latexexpr.Expression('e1', x**3 - x**2 + x - 1) 
		>>> print lsympy.factor(e1)
		e1 = \left( {1} + { {x} }^{ {2} } \right) \cdot \left( {-1} + {x} \right)
		>>> e2 = latexexpr.Expression('e2', x**2*z + 4*x*y*z + 4*y**2*z) 
		>>> print lsympy.factor(e2)
		e2 = {z} \cdot { {2} \cdot {y} + {x} }^{ {2} }
	"""
	if isinstance(arg,latexexpr.Variable):
		return arg
	if isinstance(arg,latexexpr.Expression):
		ret = copy.copy(arg)
		ret.factor(substituteFloats,**kw)
		return ret
	if isinstance(arg,latexexpr.Operation):
		s,lVars = _operation2sympy(arg,substituteFloats=substituteFloats)
		s = sympy.factor(s,**kw)
		return _sympy2operation(s,lVars)
	raise TypeError, "Unsupported type (%s) for factor"%(arg.__class__.__name__)

latexexpr.Expression.factor = lambda self,substituteFloats=False,**kw: _setOperation(self,factor(self.operation,substituteFloats=substituteFloats,**kw))

latexexpr.Operation.factor = lambda self,substituteFloats=False,**kw: _copyOperation(self,factor(self,substituteFloats=substituteFloats,**kw))

def collect(arg,syms,substituteFloats=False,**kw):
	r"""Performs collect operation on arg. Symbolic variables are left symbolic, but variables with values are treated as the values (!)
	
	:param Variable|Operation|Expression arg: argument to be processed
	:param Variable|[Variable] syms: variables to be collected
	:param bool substituteFloats: non-symbolic variables are treated as their float values if True, they are left otherwise
	:param \*\*kw: keywords for sympy.collect() function
	:rtype: type(arg)
	
	.. code-block:: python
	
		>>> import latexexpr.sympy as lsympy 
		>>> x = latexexpr.Variable('x',None) 
		>>> y = latexexpr.Variable('y',None) 
		>>> z = latexexpr.Variable('z',None) 
		>>> e1 = latexexpr.Expression('e1', x*y + x - 3  + 2*x**2 - z*x**2 + x**3) 
		>>> print lsympy.collect(e1,x)
		e1 = {-3} + { {x} }^{ {3} } + {x} \cdot \left( {1} + {y} \right) + { {x} }^{ {2} } \cdot \left( {2} - {z} \right)
	"""
	if isinstance(arg,latexexpr.Variable):
		return arg
	if isinstance(arg,latexexpr.Expression):
		ret = copy.copy(arg)
		ret.collect(syms,substituteFloats,**kw)
		return ret
	if isinstance(arg,latexexpr.Operation):
		s,lVars = _operation2sympy(arg,substituteFloats=substituteFloats)
		if not (isinstance(syms,latexexpr.Variable) or all(isinstance(latexexpr.Variable(s) for s in syms))):
			raise LaTeXExpressionError, "TODO"
		syms = sympy.Symbol(syms.name) if isinstance(syms,latexexpr.Variable) else [sympy.Symbol(s.name) for s in syms]
		s = sympy.collect(s,syms,**kw)
		return _sympy2operation(s,lVars)
	raise TypeError, "Unsupported type (%s) for collect"%(arg.__class__.__name__)

latexexpr.Expression.collect = lambda self,syms,substituteFloats=False,**kw: _setOperation(self,collect(self.operation,syms,substituteFloats=substituteFloats,**kw))

latexexpr.Operation.collect = lambda self,syms,substituteFloats=False,**kw: _copyOperation(self,collect(self,syms,substituteFloats=substituteFloats,**kw))

def cancel(arg,substituteFloats=False,**kw):
	r"""Performs cancel operation on arg. Symbolic variables are left symbolic, but variables with values are treated as the values (!)
	
	:param Variable|Operation|Expression arg: argument to be processed
	:param bool substituteFloats: non-symbolic variables are treated as their float values if True, they are left otherwise
	:param \*\*kw: keywords for sympy.cancel() function
	:rtype: type(arg)
	
	.. code-block:: python
	
		>>> import latexexpr.sympy as lsympy 
		>>> x = latexexpr.Variable('x',None) 
		>>> y = latexexpr.Variable('y',None) 
		>>> z = latexexpr.Variable('z',None) 
		>>> e1 = latexexpr.Expression('e1', (x**2 + 2*x + 1) / (x**2 + x) ) 
		>>> print lsympy.cancel(e1)
		e1 = \frac{ {1} }{ {x} } \cdot \left( {1} + {x} \right)
		>>> e2 = latexexpr.Expression('e2', 1/x + (3*x/2 - 2) / (x - 4) ) 
		>>> print lsympy.cancel(e2)
		e2 = \frac{ {1} }{ {2} \cdot { {x} }^{ {2} } + {-8} \cdot {x} } \cdot \left( {-8} + {-2} \cdot {x} + {3} \cdot { {x} }^{ {2} } \right)
		>>> e3 = latexexpr.Expression('e3', (x*y**2 - 2*x*y*z + x*z**2 + y**2 - 2*y*z + z**2) / (x**2 - 1) ) 
		>>> print lsympy.cancel(e3)
		e3 = \frac{ {1} }{ {-1} + {x} } \cdot \left( { {z} }^{ {2} } + {-2} \cdot {y} \cdot {z} + { {y} }^{ {2} } \right)
	"""
	if isinstance(arg,latexexpr.Variable):
		return arg
	if isinstance(arg,latexexpr.Expression):
		ret = copy.copy(arg)
		ret.cancel(substituteFloats,**kw)
		return ret
	if isinstance(arg,latexexpr.Operation):
		s,lVars = _operation2sympy(arg,substituteFloats=substituteFloats)
		s = sympy.cancel(s,**kw)
		return _sympy2operation(s,lVars)
	raise TypeError, "Unsupported type (%s) for cancel"%(arg.__class__.__name__)

latexexpr.Expression.cancel = lambda self,substituteFloats=False,**kw: _setOperation(self,cancel(self.operation,substituteFloats=substituteFloats,**kw))

latexexpr.Operation.cancel = lambda self,substituteFloats=False,**kw: _copyOperation(self,cancel(self,substituteFloats=substituteFloats,**kw))

def apart(arg,substituteFloats=False,**kw):
	r"""Performs apart operation on arg. Symbolic variables are left symbolic, but variables with values are treated as the values (!)
	
	:param Variable|Operation|Expression arg: argument to be processed
	:param bool substituteFloats: non-symbolic variables are treated as their float values if True, they are left otherwise
	:param \*\*kw: keywords for sympy.apart() function
	:rtype: type(arg)
	
	.. code-block:: python
	
		>>> import latexexpr.sympy as lsympy 
		>>> x = latexexpr.Variable('x',None) 
		>>> e1 = latexexpr.Expression('e1', (4*x**3 + 21*x**2 + 10*x + 12) / (x**4 + 5*x**3 + 5*x**2 + 4*x) ) 
		>>> print lsympy.apart(e1)
		e1 = \frac{ {1} }{ {1} + {x} + { {x} }^{ {2} } } \cdot \left( {-1} + {2} \cdot {x} \right) + \left( - \frac{ {1} }{ {4} + {x} } \right) + {3} \cdot \frac{ {1} }{ {x} }
	"""
	if isinstance(arg,latexexpr.Variable):
		return arg
	if isinstance(arg,latexexpr.Expression):
		ret = copy.copy(arg)
		ret.apart(substituteFloats,**kw)
		return ret
	if isinstance(arg,latexexpr.Operation):
		s,lVars = _operation2sympy(arg,substituteFloats=substituteFloats)
		s = sympy.apart(s,**kw)
		return _sympy2operation(s,lVars)
	raise TypeError, "Unsupported type (%s) for apart"%(arg.__class__.__name__)

latexexpr.Expression.apart = lambda self,substituteFloats=False,**kw: _setOperation(self,apart(self.operation,substituteFloats=substituteFloats,**kw))

latexexpr.Operation.apart = lambda self,substituteFloats=False,**kw: _copyOperation(self,apart(self,substituteFloats=substituteFloats,**kw))


# TODO other simplify-like functions?

def _setOperation(expr,operation):
	expr.operation = operation

def _copyOperation(o1,o2):
	o1.type = o2.type
	o1.args = o2.args
	o1.format = o2.format
	o1.exponent = o2.exponent







# TESTING
if __name__ == "__main__":

	import latexexpr.sympy as lsympy
	v1 = latexexpr.Variable('v1',None)
	v2 = latexexpr.Variable('v2',None)
	v3 = latexexpr.Variable('v3',1.23)
	v4 = latexexpr.Variable('v4',4.56)
	x = latexexpr.Variable('x',None)
	e1 = latexexpr.Expression('e1',v1+v1+v2+v3+v2+v3-v4)
	print e1
	print lsympy.simplify(e1)
	print lsympy.simplify(e1,substituteFloats=True)
	e1.simplify()
	print e1
	e1.simplify(substituteFloats=True)
	print e1
	e2 = latexexpr.Expression('e2',latexexpr.SIN(x)**2+latexexpr.COS(x)**2)
	print lsympy.simplify(e2)
	e3 = latexexpr.Expression('e3', (x**3 + x**2 - x - 1) / (x**2 + 2*x + 1) )
	print lsympy.simplify(e3)

	import latexexpr.sympy as lsympy
	v1 = latexexpr.Variable('v1',None)
	v2 = latexexpr.Variable('v2',None)
	v3 = latexexpr.Variable('v3',1.23)
	v4 = latexexpr.Variable('v4',4.56)
	x = latexexpr.Variable('x',None)
	e1 = latexexpr.Expression('e1',v1+v1+v2+v3+v2+v3-v4)
	print e1
	print lsympy.simplify(e1)
	print lsympy.simplify(e1,substituteFloats=True)
	e1.simplify()
	print e1
	e1.simplify(substituteFloats=True)
	print e1
	e2 = latexexpr.Expression('e2',latexexpr.SIN(x)**2+latexexpr.COS(x)**2)
	print lsympy.simplify(e2)
	e3 = latexexpr.Expression('e3', (x**3 + x**2 - x - 1) / (x**2 + 2*x + 1) )
	print lsympy.simplify(e3)

	import latexexpr.sympy as lsympy
	x = latexexpr.Variable('x',None)
	e1 = latexexpr.Expression('e1', (x+1)**2 )
	print lsympy.expand(e1,substituteFloats=True)
	e2 = latexexpr.Expression('e2', (x+2)*(x-3) )
	print lsympy.expand(e2)
	e3 = latexexpr.Expression('e3', (x+1)*(x-2) - (x-1)*x )
	print lsympy.expand(e3)

	import latexexpr.sympy as lsympy
	x = latexexpr.Variable('x',None)
	y = latexexpr.Variable('y',None)
	z = latexexpr.Variable('z',None)
	e1 = latexexpr.Expression('e1', x**3 - x**2 + x - 1)
	print lsympy.factor(e1)
	e2 = latexexpr.Expression('e2', x**2*z + 4*x*y*z + 4*y**2*z)
	print lsympy.factor(e2)

	import latexexpr.sympy as lsympy
	x = latexexpr.Variable('x',None)
	y = latexexpr.Variable('y',None)
	z = latexexpr.Variable('z',None)
	e1 = latexexpr.Expression('e1', x*y + x - 3  + 2*x**2 - z*x**2 + x**3)
	print lsympy.collect(e1,x)

	import latexexpr.sympy as lsympy
	x = latexexpr.Variable('x',None)
	y = latexexpr.Variable('y',None)
	z = latexexpr.Variable('z',None)
	e1 = latexexpr.Expression('e1', (x**2 + 2*x + 1) / (x**2 + x) )
	print lsympy.cancel(e1)
	e2 = latexexpr.Expression('e2', 1/x + (3*x/2 - 2) / (x - 4) )
	print lsympy.cancel(e2)
	e3 = latexexpr.Expression('e3', (x*y**2 - 2*x*y*z + x*z**2 + y**2 - 2*y*z + z**2) / (x**2 - 1) )
	print lsympy.cancel(e3)

	import latexexpr.sympy as lsympy
	x = latexexpr.Variable('x',None)
	e1 = latexexpr.Expression('e1', (4*x**3 + 21*x**2 + 10*x + 12) / (x**4 + 5*x**3 + 5*x**2 + 4*x) )
	print lsympy.apart(e1)
######################################################################
