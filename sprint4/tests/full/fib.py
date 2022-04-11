def fib(x: int) -> int:
	result: int
	if x <= 1:
		result = x
	else:
		result = fib(x - 1) + fib(x - 2)
	return result

print(fib(10))
