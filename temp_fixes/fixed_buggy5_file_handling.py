def read_data():
    try:
        with open("nonexistent_file.txt", 'r') as f:
            content = f.read()
    except FileNotFoundError:
        content = 'File not found. Using default content.'
    return content

print(read_data())