def save_to_file(data, filename):
    with open(filename, 'w') as file:
        file.write(str(data))
