import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QVBoxLayout, QHBoxLayout, QSplitter,
                             QPushButton, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QSettings
from notes_list import NotesList
from note_editor import NoteEditor

class NotesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("NotesApp", "SimpleNotes")
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Simple Notes")
        self.setGeometry(100, 100, 900, 600)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        
        # Панель инструментов
        toolbar_layout = QHBoxLayout()
        
        self.new_btn = QPushButton("➕ Новая")
        self.new_btn.clicked.connect(self.new_note)
        
        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.clicked.connect(self.delete_note)
        
        self.export_btn = QPushButton("📤 Экспорт")
        self.export_btn.clicked.connect(self.export_note)
        
        self.search_btn = QPushButton("🔍 Поиск")
        self.search_btn.clicked.connect(self.search_notes)
        
        toolbar_layout.addWidget(self.new_btn)
        toolbar_layout.addWidget(self.delete_btn)
        toolbar_layout.addWidget(self.export_btn)
        toolbar_layout.addWidget(self.search_btn)
        toolbar_layout.addStretch()
        
        main_layout.addLayout(toolbar_layout)
        
        # Разделитель: список заметок и редактор
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Список заметок
        self.notes_list = NotesList()
        self.notes_list.note_selected.connect(self.load_note)
        
        # Редактор заметок
        self.note_editor = NoteEditor()
        self.note_editor.note_saved.connect(self.update_notes_list)
        
        splitter.addWidget(self.notes_list)
        splitter.addWidget(self.note_editor)
        splitter.setSizes([300, 600])
        
        main_layout.addWidget(splitter)
        
        # Загрузка заметок
        self.notes_list.load_notes()
    
    def load_settings(self):
        """Загрузка настроек"""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
    
    def new_note(self):
        """Создание новой заметки"""
        self.note_editor.new_note()
    
    def delete_note(self):
        """Удаление заметки"""
        current_id = self.notes_list.get_selected_note_id()
        if current_id:
            reply = QMessageBox.question(
                self, "Удаление",
                "Удалить выбранную заметку?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.notes_list.delete_note(current_id)
                self.note_editor.clear()
        else:
            QMessageBox.warning(self, "Внимание", "Выберите заметку для удаления")
    
    def export_note(self):
        """Экспорт заметки в файл"""
        content = self.note_editor.get_content()
        title = self.note_editor.get_title()
        
        if not title or not content:
            QMessageBox.warning(self, "Внимание", "Нет заметки для экспорта")
            return
        
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Экспорт заметки",
            f"{title}.txt",
            "Text Files (*.txt);;Markdown (*.md);;All Files (*)"
        )
        
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(f"# {title}\n\n{content}")
                QMessageBox.information(self, "Успех", "Заметка экспортирована")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать: {str(e)}")
    
    def search_notes(self):
        """Поиск заметок"""
        text, ok = QInputDialog.getText(self, "Поиск", "Введите текст для поиска:")
        if ok and text:
            self.notes_list.search_notes(text)
    
    def load_note(self, note_id, title, content):
        """Загрузка заметки в редактор"""
        self.note_editor.load_note(note_id, title, content)
    
    def update_notes_list(self):
        """Обновление списка заметок"""
        self.notes_list.load_notes()
    
    def closeEvent(self, event):
        """Сохранение настроек при закрытии"""
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Загрузка стилей
    if os.path.exists("styles.qss"):
        with open("styles.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    
    window = NotesApp()
    window.show()
    sys.exit(app.exec())
