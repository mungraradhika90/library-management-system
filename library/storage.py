import json

def save_data(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=3)
        
def load_data(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}