from gurobipy import GRB, Model, quicksum
import json

modelo = Model("Entrega Optimizacion")

with open('datos.json', 'r') as f:
    datos = json.load(f)
alfa, gamma, tractor, afinidad, exp = datos['alfa']/10, datos['gamma'], datos['tractor'], datos['afinidad'], datos['experiencia']
n = 5 #bines por dia por trabajador
p = 16000 #minimo de bines
T = 30
trabajador = list(range(0, 40))
dias = list(range(0, T))
cuadrilla = list(range(0, 40//6))

J = 6
K = 8
x = modelo.addVars(dias, trabajador, cuadrilla, name="X", vtype=GRB.BINARY)
y = modelo.addVars(dias, trabajador, cuadrilla, name="Y", vtype=GRB.BINARY)
z = modelo.addVars(dias, trabajador, name="Z", vtype=GRB.BINARY)
l = modelo.addVars(dias, trabajador, name="L", vtype=GRB.BINARY)
w = modelo.addVars(dias, trabajador, name="W", vtype=GRB.BINARY)
r = modelo.addVars(dias, trabajador, cuadrilla, name="R", vtype=GRB.BINARY)
u = modelo.addVars(dias, trabajador, trabajador, cuadrilla, name="U", vtype=GRB.BINARY)
h = modelo.addVars(dias, trabajador, name="H", lb=0, ub=1)
s = modelo.addVars(dias, trabajador, name="S", lb=0, ub=1)
modelo.update()
modelo.setObjective(n * quicksum((
                  quicksum((
                  quicksum((
                      x[t, i, c] + s[t, i] + alfa * quicksum((
                        afinidad[i][j] * u[t, i, j, c] for j in trabajador if i!=j
                      ))
                  for i in trabajador))
for c in cuadrilla))
for t in dias)), GRB.MAXIMIZE)
modelo.update()
"""
for i in trabajador:
    for t in dias:
        if t <= T - 7:
            print(*range(t, t + 7))
            print([l[ti, i] for ti in range(t, t + 7)])
input()"""
#Asignacion de trabajo y dias libres
modelo.addConstrs(((1 == w[t, i] + z[t, i] + l[t, i] +
                  quicksum((x[t, i, c] for c in cuadrilla)) for t in dias for i in trabajador)))

#A lo más 3 cuadrillas por supervisor
modelo.addConstrs((quicksum((y[t, i, c] for c in cuadrilla)) <= 3 * w[t, i] for t in dias for i in  trabajador))

#Cuadrillas de 4 a 6 personas
modelo.addConstrs((4 <= quicksum((x[t, i, c] for i in trabajador)) <= 6 for t in dias for c in cuadrilla))

#Un dia de descanso por semana
modelo.addConstrs((1 == quicksum((l[ti, i] for ti in range(t, t + 7))) for i in trabajador for t in dias if t <= T - 7))



#Un capitan por cuadrilla
modelo.addConstrs((quicksum((r[t, i, c] for i in trabajador)) == 1 for t in dias for c in cuadrilla))

#Un tractorista necesita saber manejar un tractor
modelo.addConstrs((z[t, i] <= tractor[i] for t in dias for i in trabajador))

#Los capitanes tienen que ser más experimentados que su cuadrilla
modelo.addConstrs((x[t, i, c] * exp[i] <= r[t, j, c] * exp[j] for c in cuadrilla for i in trabajador for j in trabajador for t in dias if i != j ))

#Los supervisores tienen que ser más experimentados que los capitanes
modelo.addConstrs((r[t, i, c] * exp[i] <= y[t, j, c] * exp[j] for c in cuadrilla for i in trabajador for j in trabajador for t in dias if i != j ))

#Se necesitan K tractoristas
modelo.addConstrs((quicksum((z[t, i] for i in trabajador)) == K for t in dias))

#Se necesitan B supervisores
modelo.addConstrs((quicksum((l[t, i] for i in trabajador)) <= J for t in dias))

#Se necesitan Q extractores
#modelo.addConstrs((quicksum((w[t, i]for i in trabajador)) == Q for t in dias))

#Cumplir el requisito de producción
"""
modelo.addConstrs(p <= n * quicksum((
                  quicksum((
                  quicksum((
                      x[t, i, c] + s[t, i] + alfa * quicksum((
                        afinidad[i][j] * u[t, i, j, c] for j in trabajador if i != j
                      ))
                       for i in trabajador))
                       for c in cuadrilla))
                       for t in dias)))"""

#Mejora de habilidad por día trabajado
modelo.addConstrs((h[t, i] == h[t - 1,i ] + gamma * quicksum((x[t - 1, i, c] for c in cuadrilla)) for i in trabajador for t in dias if 1 <= t ))
modelo.addConstrs((h[0 ,i] == exp[i] for i in trabajador))

#Definicion variable S
modelo.addConstrs((s[t,i] <= h[t,i] for i in trabajador for t in dias))
modelo.addConstrs((s[t,i] <= x[t,i,c] for i in trabajador for t in dias for c in cuadrilla))

#Maximo de bonus por afinidad

modelo.update()
modelo.optimize()
modelo.printAttr("X")
