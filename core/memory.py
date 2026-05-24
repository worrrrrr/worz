import json, os

class Memory:
    def __init__(self, path="data/memory.json"):
        self.path = path
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w") as f: json.dump({"history": [], "last_result": 0}, f)

    def save(self, key, value):
        data = self.load_all()
        data[key] = value
        with open(self.path, "w") as f: json.dump(data, f, indent=4)

    def load_all(self):
        try:
            with open(self.path, "r") as f: return json.load(f)
        except: return {"history": [], "last_result": 0}