import json
import os
from tkinter import messagebox

class Config:
    VALID_FIELD_TYPES = ("entry", "select", "checkbox")
    VALID_SQL_TYPES = ("TEXT", "INTEGER", "REAL", "BLOB", "VARCHAR", "CHAR", "INT", "BIGINT", "SMALLINT", "FLOAT", "DOUBLE", "DECIMAL", "DATE", "TIME", "DATETIME", "BOOLEAN")
    DEFAULT = {
        "db_path": "data.db",
        "columns": [
            {
                "title": "ID",
                "type": "entry",
                "db_type": "TEXT",
                "pattern": "^\\d{4}$",
                "required": True,
                "unique": True
            },
            {
                "title": "Title",
                "type": "entry",
                "db_type": "TEXT",
                "required": True
            },
            {
                "title": "Description",
                "type": "entry",
                "db_type": "TEXT"
            },
            {
                "title": "Type",
                "type": "select",
                "values": [
                    "HDD",
                    "SSD",
                    "Flash Drive",
                    "Memory Card"
                ],
                "db_type": "TEXT",
                "required": True
            },
            {
                "title": "Is Encrypted",
                "type": "checkbox",
                "db_type": "INTEGER"
            }
        ]
    }
    def __init__(self, file_path, root):
        self.root = root
        self.path = file_path
        self.CONFIG = {}
        self.load()
    
    def load(self):
        try:
            with open(self.path, "r") as config_file:
                self.CONFIG = json.load(config_file)
            error = self.validate(self.CONFIG)
            if error:
                if not messagebox.askyesno("Config Error", f"Config file is invalid:\n{error}\n\nDo you want to reset to default config?"):
                    self.root.destroy()
                    return
                self.save(self.DEFAULT)
                self.CONFIG = self.DEFAULT.copy()
        except FileNotFoundError:
            with open(self.path, "w") as config_file:
                json.dump(self.DEFAULT, config_file, indent=4)
            self.CONFIG = self.DEFAULT.copy()
        except json.JSONDecodeError as e:
            if not messagebox.askyesno("Config Error", f"Config file is not valid JSON:\n{str(e)}\n\nDo you want to reset to default config?"):
                self.root.destroy()
                return
            self.save(self.DEFAULT)
            self.CONFIG = self.DEFAULT.copy()
    
    def save(self, config_dict: dict):
        with open(self.path, "w") as config_file:
            json.dump(config_dict, config_file, indent=4)

    def get(self, key):
        return self.CONFIG[key]
    
    def load_raw(self):
        with open(self.path, "r") as config_file:
            raw = config_file.read()
        return raw
    
    @staticmethod
    def validate(config_dict: dict) -> str | None:
        """Validate config dictionary. Returns None if valid, error message if invalid."""
        
        # Check required keys
        if not isinstance(config_dict, dict):
            return "Config must be a dictionary"
        
        if "db_path" not in config_dict:
            return "Missing required key: 'db_path'"
        
        if "columns" not in config_dict:
            return "Missing required key: 'columns'"
        
        # Validate db_path
        db_path = config_dict["db_path"]
        if not isinstance(db_path, str):
            return "db_path must be a string"
        
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            return f"db_path directory does not exist: {db_dir}"
        
        # Validate columns
        columns = config_dict["columns"]
        if not isinstance(columns, list):
            return "columns must be a list"
        
        if len(columns) == 0:
            return "columns list must have at least one element"
        
        # Validate each column
        for idx, col in enumerate(columns):
            if not isinstance(col, dict):
                return f"Column at index {idx} must be a dictionary"
            
            # Check required keys
            if "title" not in col:
                return f"Column at index {idx} missing key: 'title'"
            
            if "type" not in col:
                return f"Column at index {idx} missing key: 'type'"
            
            if "db_type" not in col:
                return f"Column at index {idx} missing key: 'db_type'"
            
            # Validate type
            col_type = col["type"]
            if col_type not in Config.VALID_FIELD_TYPES:
                return f"Column '{col['title']}': invalid type '{col_type}'. Must be one of: {', '.join(Config.VALID_FIELD_TYPES)}"
            
            # Validate db_type (case-sensitive)
            db_type = col["db_type"]
            if db_type not in Config.VALID_SQL_TYPES:
                return f"Column '{col['title']}': invalid db_type '{db_type}'. Must be a valid SQL type"
            
            # Validate select type has values
            if col_type == "select":
                if "values" not in col:
                    return f"Column '{col['title']}': 'select' type must have 'values' key"
                
                values = col["values"]
                if not isinstance(values, list):
                    return f"Column '{col['title']}': 'values' must be a list"
                
                if len(values) == 0:
                    return f"Column '{col['title']}': 'values' list must have at least one element"
        
        return None