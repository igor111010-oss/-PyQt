import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class Database:
    def __init__(self, db_name="notes.db"):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        """Инициализация базы данных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица заметок
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tags TEXT,
                    is_favorite BOOLEAN DEFAULT 0
                )
            ''')
            
            # Таблица тегов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            ''')
            
            conn.commit()
    
    def create_note(self, title: str, content: str = "", tags: str = "") -> int:
        """Создание новой заметки"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notes (title, content, tags, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (title, content, tags, datetime.now()))
            conn.commit()
            return cursor.lastrowid
    
    def update_note(self, note_id: int, title: str, content: str, tags: str = ""):
        """Обновление заметки"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE notes 
                SET title = ?, content = ?, tags = ?, updated_at = ?
                WHERE id = ?
            ''', (title, content, tags, datetime.now(), note_id))
            conn.commit()
    
    def delete_note(self, note_id: int):
        """Удаление заметки"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
    
    def get_note(self, note_id: int) -> Optional[Dict]:
        """Получение заметки по ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def get_all_notes(self, search: str = "", tag: str = "") -> List[Dict]:
        """Получение всех заметок"""
        query = "SELECT * FROM notes WHERE 1=1"
        params = []
        
        if search:
            query += " AND (title LIKE ? OR content LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        if tag:
            query += " AND tags LIKE ?"
            params.append(f"%{tag}%")
        
        query += " ORDER BY updated_at DESC"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def toggle_favorite(self, note_id: int):
        """Изменение статуса избранного"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE notes 
                SET is_favorite = NOT is_favorite 
                WHERE id = ?
            ''', (note_id,))
            conn.commit()
    
    def get_stats(self) -> Dict:
        """Получение статистики"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM notes")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM notes WHERE is_favorite = 1")
            favorites = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT tags) FROM notes")
            unique_tags = cursor.fetchone()[0]
            
            return {
                "total": total,
                "favorites": favorites,
                "unique_tags": unique_tags
            }
