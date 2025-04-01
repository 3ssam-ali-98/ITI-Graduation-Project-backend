from django.test import TestCase

# Create your tests here.
def calculate_percentage(prev, current):
	if prev == 0:
		return "100.00% increase" if current > 0 else "0.00% increase"

	prcent = (((current*10) - (prev*10)) / abs((prev*10))) * 100 

	if prcent > 0:
		return f"{prcent:.2f}% increase"
	elif prcent < 0:
		return f"{abs(prcent):.2f}% decrease"
	else:
		return "0.00% change"

print(calculate_percentage(0, 10))  # 100.00% increase
print(calculate_percentage(10, 0))  # 100.00% decrease
print(calculate_percentage(10, 20))  # 100.00% increase
print(calculate_percentage(20, 10))  # 50.00% decrease
print(calculate_percentage(10, 10))  # 0.00% change
print(calculate_percentage(0, 0))  # 0.00% change
print(calculate_percentage(10, 5))  # 50.00% decrease
print(calculate_percentage(5, 10))  # 100.00% increase
print(calculate_percentage(10, 15))  # 50.00% increase
print(calculate_percentage(15, 10))  # 33.33% decrease
print(calculate_percentage(0, 1))  # 0.00% change
print(calculate_percentage(1, 0))  # 100.00% increase
print(calculate_percentage(3, 1))  # 100.00% decrease
print(calculate_percentage(10, 1))  # 100.00% increase
print(calculate_percentage(1, 10))  # 50.00% decrease
print(calculate_percentage(1, 1))  # 0.00% change