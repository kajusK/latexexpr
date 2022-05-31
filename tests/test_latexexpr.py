from latexexpr import Expression, Variable

def test_variable():
    v1 = Variable('H_{ello}',3.25,'m')
    assert str(v1) == 'H_{ello} = 3.25 \\ \\mathrm{m}'

def test_expression():
    v1 = Variable('H_{ello}',3.25,'m')
    v2 = Variable('W^{orld}',5.63,'m')
    e1 = Expression('E_{xample}',v1+v2,'m')
    assert str(e1) == 'E_{xample} = {H_{ello}} + {W^{orld}} = 3.25 + 5.63 = 8.88 \\ \\mathrm{m}'
