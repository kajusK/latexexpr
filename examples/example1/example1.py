import latexexpr
v1 = latexexpr.Variable('H_{ello}',3.25,'m')
print(f'$$ {v1} $$')
v2 = latexexpr.Variable('W^{orld}',5.63,'m')
print(f'$$ {v2} $$')
e1 = latexexpr.Expression('E_{xample}',v1+v2,'m')
print('$$ {e1} $$')
