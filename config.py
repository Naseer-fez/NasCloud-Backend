import json

class Config:
    def __init__(self):
        self.reload()
        
    def reload(self):
        with open("config.json") as file:
            self.data=json.load(file)
            
    def get(self, key, default=None):
        return self.data.get(key, default)
        
config = Config()



