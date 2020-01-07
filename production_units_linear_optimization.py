from pyomo.environ import *
from pyomo.opt import SolverFactory

price_reg = 24 * 1000  # cost to produce a unit per month
price_ovrtm = 38 * 1000  # cost is raised to this level to produce a unit in overtime
price_merchant = 3 * 1000  # cost to stock a unit per month
volume = 40  # volume in thousands

#the empirical demand per each of 12 months
spros = [
    18.0, 17.0, 14.0, 22.0, 35.0, 47.0, 55.0, 39.0, 28.0, 10.0, 17.0, 22.0
]
number = len(spros)

md = Concretemd(name="Bicycle")
md.time = RangeSet(1, number)
md.store_time = RangeSet(0, number)
md.prod_normal = Var(md.time, bounds=(0, volume))
md.prod_overtime = Var(md.time, bounds=(0, volume / 2))
md.store = Var(md.store_time, within=NonNegativeReals)

md.obj = Objective(
    expr=sum(price_reg * md.prod_normal[i] +
             price_ovrtm * md.prod_overtime[i] + price_merchant * md.store[i]
             for i in md.time),
    sense=minimize)


def temporal_restriction(md, t):
    intake = md.prod_normal[t] + md.prod_overtime[t] + md.store[t - 1]
    outgoing = spros[t - 1] + md.store[t]
    return intake == outgoing


md.constr = Constraint(md.time, rule=temporal_restriction)
md.store[0].fix(2.0)

solver = SolverFactory("glpk")
results = solver.solve(md)
print(results)
md.pprint()

print("spros\tnormal\tover\tstore")
#at the end of each period we have 13 numbers indicating the stock level
for t in range(1, 13):
    print("{:4}\t{:4}\t{:4}\t{:4}".format(spros[t - 1],
                                          value(md.prod_normal[t]),
                                          value(md.prod_overtime[t]),
                                          value(md.store[t])))
