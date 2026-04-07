from core.config import Config
from core.db import DB

class Store:
    def __init__(self, root):
        self.root = root
        self.config = Config("config.json", root)
        self.db = DB(self.config.get("db_path"), self.config.get("columns"))
        self.table = None
        self.selected = None