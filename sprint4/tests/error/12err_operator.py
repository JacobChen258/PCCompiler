# Our language does not support type casting
#
def i_func() -> int:
	return 1

def f_func() -> float:
	return 1.0

x: int = i_func()
y: float = f_func()
a: float = x + y
