from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, 
                             QListWidgetItem, QLabel, QHBoxLayout,
                             QPushButton, QMenu, QInputDialog)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QAction, QIcon
from database import Database

class NotesList(QWidget):
    note_selected = pyqtSignal(int, str, str)  # id, title, content
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_search = ""
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Заголовок
        title_layout = QHBoxLayout()
        self.title_label = QLabel("📝 Заметки")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        
        # Кнопка обновления
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.clicked.connect(self.load_notes)
        self.refresh_btn.setFixedSize(30, 30)
        title_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(title_layout)
        
        # Список заметок
        self.notes_list = QListWidget()
        self.notes_list.itemClicked.connect(self.on_note_clicked)
        self.notes_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.notes_list.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.notes_list)
        
        # Статистика
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(self.stats_label)
    
    def load_notes(self, search: str = ""):
        """Загрузка заметок"""
        self.current_search = search
        self.notes_list.clear()
        
        notes = self.db.get_all_notes(search)
        
        for note in notes:
            item = QListWidgetItem()
            
            # Создание виджета для элемента списка
            widget = QWidget()
            item_layout = QVBoxLayout(widget)
            
            # Заголовок
            title = QLabel(note['title'][:50] + ("..." if len(note['title']) > 50 else ""))
            title.setStyleSheet("font-weight: bold;")
            
            # Время изменения
            time_str = note['updated_at'][:16] if note['updated_at'] else ""
            time_label = QLabel(time_str)
            time_label.setStyleSheet("color: gray; font-size: 11px;")
            
            # Теги
            tags = note.get('tags', '')
            if tags:
                tags_label = QLabel(f"🏷️ {tags}")
                tags_label.setStyleSheet("color: #2196F3; font-size: 11px;")
                item_layout.addWidget(tags_label)
            
            item_layout.addWidget(title)
            item_layout.addWidget(time_label)
            
            if note.get('is_favorite'):
                title.setStyleSheet("font-weight: bold; color: #FF9800;")
            
            widget.setLayout(item_layout)
            item.setSizeHint(widget.sizeHint())
            
            # Сохраняем ID заметки в данные элемента
            item.setData(Qt.ItemDataRole.UserRole, note['id'])
            self.notes_list.addItem(item)
            self.notes_list.setItemWidget(item, widget)
        
        # Обновление статистики
        stats = self.db.get_stats()
        self.stats_label.setText(f"Всего: {stats['total']} | Избранных: {stats['favorites']}")
    
    def on_note_clicked(self, item):
        """Обработка клика по заметке"""
        note_id = item.data(Qt.ItemDataRole.UserRole)
        note = self.db.get_note(note_id)
        
        if note:
            self.note_selected.emit(
                note['id'],
                note['title'],
                note['content'] or ""
            )
    
    def get_selected_note_id(self) -> int:
        """Получение ID выбранной заметки"""
        current_item = self.notes_list.currentItem()
        if current_item:
            return current_item.data(Qt.ItemDataRole.UserRole)
        return 0
    
    def delete_note(self, note_id: int):
        """Удаление заметки"""
        self.db.delete_note(note_id)
        self.load_notes(self.current_search)
    
    def toggle_favorite(self):
        """Изменение статуса избранного"""
        note_id = self.get_selected_note_id()
        if note_id:
            self.db.toggle_favorite(note_id)
            self.load_notes(self.current_search)
    
    def add_tag(self):
        """Добавление тега к заметке"""
        note_id = self.get_selected_note_id()
        if note_id:
            tag, ok = QInputDialog.getText(self, "Добавить тег", "Введите тег:")
            if ok and tag:
                note = self.db.get_note(note_id)
                current_tags = note.get('tags', '')
                new_tags = f"{current_tags},{tag}" if current_tags else tag
                self.db.update_note(note_id, note['title'], note['content'], new_tags)
                self.load_notes(self.current_search)
    
    def search_notes(self, text: str):
        """Поиск заметок"""
        self.load_notes(text)
    
    def show_context_menu(self, position):
        """Показать контекстное меню"""
        if self.notes_list.currentItem():
            menu = QMenu()
            
            favorite_action = QAction("⭐ Избранное", self)
            favorite_action.triggered.connect(self.toggle_favorite)
            menu.addAction(favorite_action)
            
            tag_action = QAction("🏷️ Добавить тег", self)
            tag_action.triggered.connect(self.add_tag)
            menu.addAction(tag_action)
            
            menu.addSeparator()
            
            delete_action = QAction("🗑️ Удалить", self)
            delete_action.triggered.connect(lambda: self.delete_note(self.get_selected_note_id()))
            menu.addAction(delete_action)
            
            menu.exec(self.notes_list.mapToGlobal(position))
