a: [int] = [1,2,3]
b: [float] = [1.0,2.0,3.0]
c: [int] = []

result1: int = 0
for v in a:
	result1 = result1 + v

result2: float = 0
for v in b:
	result2 = result2 + v

result3: int = 0
for v in c:
	result3 = result3 + v

for i in range(20):
	result1 = result1 + i

for i in range(-20, 20):
	result1 = result1 + i

for i in range(-20, 20, 4):
	result1 = result1 + i
