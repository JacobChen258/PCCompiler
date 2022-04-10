# Operator type error involving variable with inferred type
#
s: str = 'hi'
for v in [1]:
	v = v + s
