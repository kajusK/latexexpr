# LaTeX Expression

The *LaTex Expression* is a python module for easy LaTeX typesetting of algebraic
expressions in symbolic form with automatic substitution and result computation.

It was originally written by [Jan Stransky](https://mech.fsv.cvut.cz/~stransky)
from Czech Technical University, Faculty of Civil Engineering, Department of
Structural Mechanics, but the latest update was done in 2015.

## Usage
Install using pip
```
pip install latexexpr
```

Enjoy
```
import latexexpr
v1 = latexexpr.Variable('H_{ello}',3.25,'m')
print(f'$$ {v1} $$')
v2 = latexexpr.Variable('W^{orld}',5.63,'m')
print(f'$$ {v2} $$')
e1 = latexexpr.Expression('E_{xample}',v1+v2,'m')
print(f'$$ {e1} $$')
```

## Links
* [Original webpage](https://mech.fsv.cvut.cz/~stransky/en/software/latexexpr/)
* [Original documentation](https://mech.fsv.cvut.cz/~stransky/software/latexexpr/doc/index.html)


## License
The project is released under [LGPL v3](https://www.gnu.org/licenses/lgpl-3.0.en.html)
