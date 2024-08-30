import pyomo.environ as pyo
from pyomo.opt import SolverFactory

m = pyo.ConcreteModel()

#sets of points
m.setAllPoints = ['A','P1','P2','P3','B']
m.setPoints = ['P1','P2','P3']

#sets of routes from to
m.setRoutes = [['A','P1'],['A','P2'],['P1','P2'],['P2','P1'],['P1','B'],['P2','P3'],['P3','B']]
m.setRoutes_from = {key:[] for key in m.setAllPoints}
m.setRoutes_to = {key:[] for key in m.setAllPoints}
for route in m.setRoutes:
    m.setRoutes_from[route[0]].append(route[1])
    m.setRoutes_to[route[1]].append(route[0])

#parameters
m.D = {}
m.D['A','P1'] = 2
m.D['A','P2'] = 7
m.D['P1','P2'] = 10
m.D['P2','P1'] = 10
m.D['P1','B'] = 30
m.D['P2','P3'] = 8
m.D['P3','B'] = 5

#variables
m.x = pyo.Var(m.setRoutes, within=pyo.Binary)

#objective function
m.obj = pyo.Objective(expr = sum([
    m.x[route[0], route[1]] * m.D[route[0], route[1]]
    for route in m.setRoutes
    ]), sense=pyo.minimize)

#constraints --> TIP: run the code and print m.setRoutes_from and m.setRoutes_to, and check the SETs of the problem
#you can replace m.setRoutes_from['A'] for 'P1', 'P2'], it would work for this problem, but not for a other network
m.C1 = pyo.Constraint(expr = sum([m.x['A',j] for j in m.setRoutes_from['A']]) == 1)
m.C2 = pyo.Constraint(expr = sum([m.x[i,'B'] for i in m.setRoutes_to['B']]) == 1)
m.C3 = pyo.ConstraintList()
for i in m.setPoints:
    m.C3.add(sum([m.x[i,j] for j in m.setRoutes_from[i]]) == sum([m.x[j,i] for j in m.setRoutes_to[i]]))

#solve
opt = SolverFactory('gurobi')
m.results = opt.solve(m)

#print
m.pprint()
print('\n\nOF:',pyo.value(m.obj))
for route in m.setRoutes:
    if pyo.value(m.x[route[0], route[1]]) >= 0.9:
        print('Route activated: %s-%s' % (route[0], route[1]))