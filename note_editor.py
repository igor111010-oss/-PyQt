from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, 
                             QTextEdit, QPushButton, QHBoxLayout,
                             QLabel, QMessageBox)
from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCharFormat, QColor
from database import Database
import re

class NoteEditor(QWidget):
    note_saved = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_note_id = 0
        self.is_changed = False
        self.init_ui()
        
        # Таймер автосохранения
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(30000)  # Каждые 30 секунд
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Заголовок редактора
        editor_title = QLabel("✏️ Редактор")
        editor_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(editor_title)
        
        # Поле для заголовка
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Заголовок заметки...")
        self.title_input.setStyleSheet("""
            QLineEdit {
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)
        self.title_input.textChanged.connect(self.on_content_changed)
        layout.addWidget(self.title_input)
        
        # Кнопки форматирования
        format_layout = QHBoxLayout()
        
        self.bold_btn = QPushButton("B")
        self.bold_btn.clicked.connect(self.toggle_bold)
        self.bold_btn.setFixedSize(30, 30)
        
        self.italic_btn = QPushButton("I")
        self.italic_btn.clicked.connect(self.toggle_italic)
        self.italic_btn.setFixedSize(30, 30)
        
        format_layout.addWidget(QLabel("Формат:"))
        format_layout.addWidget(self.bold_btn)
        format_layout.addWidget(self.italic_btn)
        format_layout.addStretch()
        
        layout.addLayout(format_layout)
        
        # Основное поле для текста
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Начните писать здесь...")
        self.content_edit.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
            QTextEdit:focus {
                border-color: #2196F3;
            }
        """)
        self.content_edit.textChanged.connect(self.on_content_changed)
        layout.addWidget(self.content_edit)
        
        # Панель инструментов
        toolbar_layout = QHBoxLayout()
        
        # Статус сохранения
        self.status_label = QLabel("Сохранено")
        self.status_label.setStyleSheet("color: green;")
        
        # Кнопки
        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.clicked.connect(self.save_note)
        self.save_btn.setEnabled(False)
        
        self.clear_btn = QPushButton("🗑️ Очистить")
        self.clear_btn.clicked.connect(self.clear)
        
        toolbar_layout.addWidget(self.status_label)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.save_btn)
        toolbar_layout.addWidget(self.clear_btn)
        
        layout.addLayout(toolbar_layout)
        
        # Информация о заметке
        self.info_label = QLabel()
        self.info_label.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(self.info_label)
    
    def on_content_changed(self):
        """Обработка изменения содержимого"""
        self.is_changed = True
        self.save_btn.setEnabled(True)
        self.status_label.setText("Не сохранено")
        self.status_label.setStyleSheet("color: red;")
    
    def load_note(self, note_id, title, content):
        """Загрузка заметки в редактор"""
        self.current_note_id = note_id
        self.title_input.setText(title)
        self.content_edit.setText(content)
        self.is_changed = False
        self.save_btn.setEnabled(False)
        self.status_label.setText("Сохранено")
        self.status_label.setStyleSheet("color: green;")
        
        # Обновление информации
        note = self.db.get_note(note_id)
        if note:
            created = note.get('created_at', '')[:19]
            updated = note.get('updated_at', '')[:19]
            self.info_label.setText(f"Создано: {created} | Изменено: {updated}")
    
    def new_note(self):
        """Создание новой заметки"""
        self.current_note_id = 0
        self.title_input.clear()
        self.content_edit.clear()
        self.is_changed = False
        self.save_btn.setEnabled(False)
        self.status_label.setText("Новая заметка")
        self.status_label.setStyleSheet("color: blue;")
        self.info_label.clear()
        self.title_input.setFocus()
    
    def save_note(self):
        """Сохранение заметки"""
        title = self.title_input.text().strip()
        content = self.content_edit.toPlainText().strip()
        
        if not title:
            QMessageBox.warning(self, "Ошибка", "Введите заголовок заметки")
            return
        
        try:
            if self.current_note_id:
                # Обновление существующей заметки
                self.db.update_note(self.current_note_id, title, content)
            else:
                # Создание новой заметки
                self.current_note_id = self.db.create_note(title, content)
            
            self.is_changed = False
            self.save_btn.setEnabled(False)
            self.status_label.setText("Сохранено")
            self.status_label.setStyleSheet("color: green;")
            
            # Сигнал об обновлении списка
            self.note_saved.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {str(e)}")
    
    def autosave(self):
        """Автосохранение"""
        if self.is_changed and self.title_input.text().strip():
            self.save_note()
    
    def clear(self):
        """Очистка редактора"""
        if self.is_changed:
            reply = QMessageBox.question(
                self, "Очистка",
                "У вас есть несохраненные изменения. Очистить?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        self.new_note()
    
    def get_content(self):
        """Получение содержимого заметки"""
        return self.content_edit.toPlainText()
    
    def get_title(self):
        """Получение заголовка заметки"""
        return self.title_input.text()
    
    def toggle_bold(self):
        """Переключение жирного текста"""
        cursor = self.content_edit.textCursor()
        format = QTextCharFormat()
        
        if cursor.charFormat().fontWeight() == QFont.Weight.Bold:
            format.setFontWeight(QFont.Weight.Normal)
        else:
            format.setFontWeight(QFont.Weight.Bold)
        
        cursor.mergeCharFormat(format)
    
    def toggle_italic(self):
        """Переключение курсивного текста"""
        cursor = self.content_edit.textCursor()
        format = QTextCharFormat()
        format.setFontItalic(not cursor.charFormat().fontItalic())
        cursor.mergeCharFormat(format)
