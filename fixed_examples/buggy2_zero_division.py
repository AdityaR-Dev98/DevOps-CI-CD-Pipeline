def calculate_average(numbers):
    if len(numbers)!= 0:
        return sum(numbers) / len(numbers)
    else:
        return "The list is empty"

print(calculate_average([]))