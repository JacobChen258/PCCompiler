# Incorrect type in assignment involving function return type
#
def func() -> int:
	return 1

a: str = func()
