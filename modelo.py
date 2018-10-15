input('a')
from gurobipy import GRB, Model
input('b')
#import json

modelo = Model("Entrega 2 Optimizacion")

with open('datos.json', 'r') as f:
    datos = json.load(f)
alfa, gamma, tractor, afinidad, exp = datos.values()
recoleccion_base = 5 #bines por dia por trabajador
requerido = 16000

trabajador = list(range(1, 41))
dias = list(range(1, 91))
cuadrilla = list(range(1, 40//6 + 1))

T = modelo.addVar(vtype=GRB.INTEGER, name="T", lb=1, ub=90)
x = modelo.addVars(dias, trabajador, cuadrilla, name="X", vtype=GRB.BINARY)
y = modelo.addVars(dias, trabajador, cuadrilla, name="Y", vtype=GRB.BINARY)
z = modelo.addVars(dias, trabajador, name="Z", vtype=GRB.BINARY)
l = modelo.addVars(dias, trabajador, name="L", vtype=GRB.BINARY)
w = modelo.addVars(dias, trabajador, name="W", vtype=GRB.BINARY)
r = modelo.addVars(dias, trabajador, cuadrilla, name="R", vtype=GRB.BINARY)
u = modelo.addVars(dias, trabajador, trabajador, cuadrilla, name="U", vtype=GRB.BINARY)
h = modelo.addVars(dias, trabajador, name="H", lb=0, ub=1)
modelo.setObjective(T, GRB.MINIMIZE)
modelo.update()
#Asignacion de trabajo y dias libres
modelo.addConstrs((1 == (w[t, i] + z[t, i] + l[t, i] +
                  quicksum((x[t, i, c] for c in cuadrilla)) if t <= T else
                  0 == (w[t, i] + z[t, i] + l[t, i] +
                  quicksum((x[t, i, c] for c in cuadrilla))
                     for t in dias for i in trabajador))

#A lo más 3 cuadrillas por supervisor
modelo.addConstrs((quicksum((y[t, i, c] for c in cuadrilla)) <= 3 * w[t, i] for t in dias for i in  trabajador))

#Cuadrillas de 4 a 6 personas
modelo.addConstrs((4 <= quicksum((x[t, i, c] for i in trabajador)) <= 6 if t <= T for t in dias for c in cuadrilla))

#Un dia de descanso por semana
modelo.addConstrs((quicksum(l[t1, i] for t1 in range(t, t + 7))) if t <= T-6 for i in trabajador for t in dias)

#Un capitan por cuadrilla
modelo.addConstrs((quicksum(r[t, i, c] for i in trabajador) if t <=T for t in dias for c in cuadrilla))

#Un tractorista necesita saber manejar un tractor
modelo.addConstrs((z[t, i] <= tractor[i] if t <=T for t in dias for i in trabajador ))

#Los capitanes tienen que ser más experimentados que su cuadrilla
modelo.addConstrs((x[t, i, c] * h[t, i] <= r[t, j, c] * h[t, j] if i != j and t <= T for i in trabajador for j in trabajador for t in dias))

#Los supervisores tienen que ser más experimentados que los capitanes
modelo.addConstrs((r[t, i, c] * h[t, i] <= y[t, j, c] * [t, j] if i != j and t <= T for i in trabajador for j in trabajador for t in dias))

#Se necesitan K tractoristas
modelo.addConstrs((quicksum((z[t, i] for i in trabajador)) == K  if t <= T for t in dias)

#Se necesitan B supervisores
modelo.addConstrs((quicksum((w[t, i] for i in trabajador)) == B if t <= T for t in dias)

#Se necesitan Q extractores
modelo.addConstrs((quicksum((w[t, i]for i in trabajador)) == Q if t <= T for t in dias)

#Cumplir el requisito de producción
modelo.addConstrs(recoleccion_base * (1 + quicksum((quicksum((quicksum((h[t, i]* x[t, i, c] + quicksum((afinidad[i][j] * u[t, i, j, c] * alfa if i != j for j in trabajador)) for c in cuadrilla))
for i in trabajadpr))if t <= T for t in dias))) >= requerido)

#Mejora de habilidad por día trabajado
modelo.addConstrs((h[t, i] == h[t - 1,i ] * (1 + gamma * quicksum((x[t - 1, i, c] for c in cuadrilla))) if 2 <= t <= T for i in trabajador for t in dias))
