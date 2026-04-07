import sqlite3
import re

class DB:
    TABLE_NAME = "disks"
    ID_COLUMN = "id_builtin"
    
    def __init__(self, file_path, columns):
        self.conn = sqlite3.connect(file_path)
        self.cursor = self.conn.cursor()
        self.columns = columns
        self.init_table()
    
    def _normalize_col(self, name: str) -> str:
        """Convert column name: spaces to underscores"""
        return name.replace(" ", "_")
    
    def _get_col_list(self) -> str:
        """Get comma-separated column names"""
        return ", ".join(self._normalize_col(col["title"]) for col in self.columns)
    
    def _get_col_type(self, col_name: str) -> str:
        """Get column database type from config (case-insensitive)"""
        normalized = self._normalize_col(col_name).lower()
        for col in self.columns:
            if self._normalize_col(col["title"]).lower() == normalized:
                return col.get("db_type", "TEXT")
        return "TEXT"
    
    def _should_use_lower(self, col_name: str) -> bool:
        """Check if column should use LOWER() function (TEXT columns only)"""
        col_type = self._get_col_type(col_name)
        return col_type == "TEXT"
    
    def _unquote(self, value: str) -> str:
        """Remove surrounding quotes if present"""
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            return value[1:-1]
        return value
    
    def init_table(self):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} ({self.ID_COLUMN} INTEGER PRIMARY KEY AUTOINCREMENT)")
        self.conn.commit()
        self.cursor.execute(f"PRAGMA table_info({self.TABLE_NAME})")
        existing = [row[1] for row in self.cursor.fetchall()]
        for col in self.columns:
            col_name = self._normalize_col(col["title"])
            if col_name not in existing:
                self.cursor.execute(f"ALTER TABLE {self.TABLE_NAME} ADD COLUMN {col_name} {col['db_type']}")
        self.conn.commit()
    
    def insert(self, data: dict):
        keys = [self._normalize_col(x) for x in data.keys()]
        cols = ", ".join(keys)
        placeholders = ", ".join(["?" for _ in data])
        self.cursor.execute(f"INSERT INTO {self.TABLE_NAME} ({cols}) VALUES ({placeholders})", tuple(data.values()))
        self.conn.commit()
    
    def update(self, data, id_builtin):
        keys = [f"{self._normalize_col(x)} = ?" for x in data.keys()]
        cols = ", ".join(keys)
        self.cursor.execute(f"UPDATE {self.TABLE_NAME} SET {cols} WHERE {self.ID_COLUMN} = {id_builtin}", tuple(data.values()))
    
    def fetch_all(self) -> list:
        cols = self._get_col_list()
        self.cursor.execute(f"SELECT {cols}, {self.ID_COLUMN} FROM {self.TABLE_NAME}")
        return self.cursor.fetchall()
    
    def fetch_one(self, id_builtin):
        cols = self._get_col_list()
        self.cursor.execute(f"SELECT {cols} FROM {self.TABLE_NAME} WHERE {self.ID_COLUMN} = ?", (id_builtin,))
        return self.cursor.fetchone()
    
    def search(self, query: str) -> list:
        if not query:
            return self.fetch_all()
        
        cols = self._get_col_list()
        parts = [p.strip() for p in query.split(',')]
        where_conditions = []
        params = []
        valid_cols = {self._normalize_col(col["title"]).lower() for col in self.columns}
        for part in parts:
            if not part:
                continue
            if '=' in part:
                match = re.match(r'(.+?)\s*(=|!=|<|>|<=|>=|LIKE)\s*(.+)', part, re.IGNORECASE)
                if match:
                    col_name = self._normalize_col(match.group(1).strip()).lower()
                    if col_name not in valid_cols:
                        return []
                    # Get actual column name (with original case) for query
                    actual_col_name = self._normalize_col(match.group(1).strip())
                    op = match.group(2).strip()
                    value = self._unquote(match.group(3).strip())
                    
                    # Use LOWER() only for TEXT columns
                    if self._should_use_lower(match.group(1).strip()):
                        where_conditions.append(f"LOWER({actual_col_name}) {op} LOWER(?)")
                    else:
                        where_conditions.append(f"{actual_col_name} {op} ?")
                    params.append(value)
            else:
                word_conds = [f"LOWER(CAST({self._normalize_col(col['title'])} AS TEXT)) LIKE LOWER(?)" for col in self.columns]
                where_conditions.append(f"({' OR '.join(word_conds)})")
                params.extend([f"%{part}%" for _ in self.columns])
        if not where_conditions:
            return self.fetch_all()
        where_clause = " AND ".join(where_conditions)
        self.cursor.execute(f"SELECT {cols}, {self.ID_COLUMN} FROM {self.TABLE_NAME} WHERE {where_clause}", params)
        return self.cursor.fetchall()
    
    def delete(self, id_val) -> None:
        self.cursor.execute(f"DELETE FROM {self.TABLE_NAME} WHERE {self.ID_COLUMN} = ?", (id_val,))
        self.conn.commit()
    
    def exists(self, col: str, value: str) -> bool:
        self.cursor.execute(f"SELECT 1 FROM {self.TABLE_NAME} WHERE {col} = ?", (value,))
        return self.cursor.fetchone() is not None