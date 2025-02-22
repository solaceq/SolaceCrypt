#!/usr/bin/env python3

import sys
import os
from pathlib import Path
from typing import Optional, Dict
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLineEdit, QLabel, 
                            QFileDialog, QProgressBar, QMessageBox, QStyle,
                            QStatusBar, QMenuBar, QMenu, QCheckBox, QComboBox,
                            QFrame, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPalette, QColor, QAction, QFont
from file_encryptor import SecureFileEncryptor

class ThemeManager:
    """Manage application themes"""
    
    THEMES = {
        'Dark Blue': {
            'background': "#2E2E2E",
            'foreground': "#E0E0E0",
            'accent': "#0D47A1",
            'accent_hover': "#1565C0",
            'accent_pressed': "#0A367A",
            'secondary': "#424242",
            'input_bg': "#1E1E1E",
        },
        'Dark Purple': {
            'background': "#2E2E2E",
            'foreground': "#E0E0E0",
            'accent': "#6A1B9A",
            'accent_hover': "#8E24AA",
            'accent_pressed': "#4A148C",
            'secondary': "#424242",
            'input_bg': "#1E1E1E",
        },
        'Light Blue': {
            'background': "#F5F5F5",
            'foreground': "#212121",
            'accent': "#1976D2",
            'accent_hover': "#1E88E5",
            'accent_pressed': "#1565C0",
            'secondary': "#E0E0E0",
            'input_bg': "#FFFFFF",
        },
        'Light Purple': {
            'background': "#F5F5F5",
            'foreground': "#212121",
            'accent': "#7B1FA2",
            'accent_hover': "#8E24AA",
            'accent_pressed': "#6A1B9A",
            'secondary': "#E0E0E0",
            'input_bg': "#FFFFFF",
        }
    }
    
    BUTTON_STYLES = {
        'Rounded': '8px',
        'Slightly Rounded': '4px',
        'Square': '0px'
    }

class SolaceCryptGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.current_theme = 'Dark Blue'
        self.current_button_style = 'Rounded'
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface with improved layout and styling."""
        self.setWindowTitle('SolaceCrypt')
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Add header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        # Logo/Title section
        title = QLabel('SolaceCrypt')
        title.setStyleSheet('''
            font-size: 32px;
            font-weight: bold;
            font-family: 'Segoe UI', sans-serif;
        ''')
        
        subtitle = QLabel('Secure File Encryption')
        subtitle.setStyleSheet('''
            font-size: 16px;
            color: #888888;
            font-family: 'Segoe UI', sans-serif;
        ''')
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout)
        
        # Add theme selector
        theme_layout = QHBoxLayout()
        theme_label = QLabel('Theme:')
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(ThemeManager.THEMES.keys())
        self.theme_selector.setCurrentText(self.current_theme)
        self.theme_selector.currentTextChanged.connect(self.change_theme)
        
        button_style_label = QLabel('Button Style:')
        self.button_style_selector = QComboBox()
        self.button_style_selector.addItems(ThemeManager.BUTTON_STYLES.keys())
        self.button_style_selector.setCurrentText(self.current_button_style)
        self.button_style_selector.currentTextChanged.connect(self.change_button_style)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_selector)
        theme_layout.addSpacing(20)
        theme_layout.addWidget(button_style_label)
        theme_layout.addWidget(self.button_style_selector)
        
        header_layout.addLayout(theme_layout)
        layout.addWidget(header)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # File selection section
        file_group = QWidget()
        file_layout = QVBoxLayout(file_group)
        
        file_label = QLabel('Select File')
        file_label.setStyleSheet('font-weight: bold; font-size: 14px;')
        file_layout.addWidget(file_label)
        
        file_input_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText('Drag and drop a file or click Browse...')
        self.file_path.setReadOnly(True)
        
        browse_btn = QPushButton('Browse')
        browse_btn.setFixedWidth(120)
        browse_btn.clicked.connect(self.browse_file)
        
        file_input_layout.addWidget(self.file_path)
        file_input_layout.addWidget(browse_btn)
        file_layout.addLayout(file_input_layout)
        layout.addWidget(file_group)
        
        # Passphrase section
        pass_group = QWidget()
        pass_layout = QVBoxLayout(pass_group)
        
        pass_label = QLabel('Passphrase')
        pass_label.setStyleSheet('font-weight: bold; font-size: 14px;')
        pass_layout.addWidget(pass_label)
        
        self.passphrase = QLineEdit()
        self.passphrase.setPlaceholderText('Enter a strong passphrase...')
        self.passphrase.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.show_pass = QCheckBox('Show passphrase')
        self.show_pass.stateChanged.connect(self.toggle_passphrase_visibility)
        
        pass_layout.addWidget(self.passphrase)
        pass_layout.addWidget(self.show_pass)
        layout.addWidget(pass_group)
        
        # Options section
        options_group = QWidget()
        options_layout = QVBoxLayout(options_group)
        
        options_label = QLabel('Options')
        options_label.setStyleSheet('font-weight: bold; font-size: 14px;')
        options_layout.addWidget(options_label)
        
        self.delete_original = QCheckBox('Securely delete original file after encryption')
        options_layout.addWidget(self.delete_original)
        layout.addWidget(options_group)
        
        # Action buttons
        btn_group = QWidget()
        btn_layout = QHBoxLayout(btn_group)
        btn_layout.setSpacing(15)
        
        self.encrypt_btn = QPushButton('Encrypt File')
        self.encrypt_btn.setFixedWidth(200)
        self.encrypt_btn.clicked.connect(lambda: self.process_file('encrypt'))
        
        self.decrypt_btn = QPushButton('Decrypt File')
        self.decrypt_btn.setFixedWidth(200)
        self.decrypt_btn.clicked.connect(lambda: self.process_file('decrypt'))
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.encrypt_btn)
        btn_layout.addWidget(self.decrypt_btn)
        btn_layout.addStretch()
        layout.addWidget(btn_group)
        
        # Progress section
        progress_group = QWidget()
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setFixedHeight(8)
        progress_layout.addWidget(self.progress)
        
        layout.addWidget(progress_group)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Apply initial theme
        self.change_theme(self.current_theme)

    def change_theme(self, theme_name):
        """Apply selected theme to the application."""
        theme = ThemeManager.THEMES[theme_name]
        self.current_theme = theme_name
        
        # Create base stylesheet
        base_style = f"""
            QMainWindow {{
                background-color: {theme['background']};
                color: {theme['foreground']};
            }}
            QPushButton {{
                background-color: {theme['accent']};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: {ThemeManager.BUTTON_STYLES[self.current_button_style]};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme['accent_hover']};
            }}
            QPushButton:pressed {{
                background-color: {theme['accent_pressed']};
            }}
            QLineEdit {{
                padding: 10px;
                border: 1px solid {theme['secondary']};
                border-radius: 4px;
                background-color: {theme['input_bg']};
                color: {theme['foreground']};
            }}
            QLabel {{
                color: {theme['foreground']};
            }}
            QCheckBox {{
                color: {theme['foreground']};
                spacing: 8px;
            }}
            QProgressBar {{
                border: none;
                background-color: {theme['secondary']};
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {theme['accent']};
                border-radius: 4px;
            }}
            QComboBox {{
                padding: 5px 10px;
                border: 1px solid {theme['secondary']};
                border-radius: 4px;
                background-color: {theme['input_bg']};
                color: {theme['foreground']};
            }}
        """
        
        self.setStyleSheet(base_style)

    def change_button_style(self, style_name):
        """Change button corner style."""
        self.current_button_style = style_name
        self.change_theme(self.current_theme)  # Reapply theme with new button style

    def browse_file(self):
        # Implement file browsing functionality
        pass

    def toggle_passphrase_visibility(self):
        # Implement passphrase visibility toggle functionality
        pass

    def process_file(self, operation):
        # Implement file processing functionality
        pass 