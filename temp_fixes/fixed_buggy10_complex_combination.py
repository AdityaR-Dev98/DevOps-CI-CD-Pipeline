def process_data(data):
    avg = sum(data) / len(data)
    with open("config.json") as f:
        config = json.load(f)
    print("Configuration loaded:", config["version"])
    return avg * config["scale"]

numbers = [1, 2, 3, 4, 5]
result = process_data(numbers)
print("Result:", result)