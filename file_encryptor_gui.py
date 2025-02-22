#!/usr/bin/env python3

import sys
import os
from pathlib import Path
from typing import Optional, Dict
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLineEdit, QLabel, 
                            QFileDialog, QProgressBar, QMessageBox, QStyle,
                            QStatusBar, QMenuBar, QMenu, QCheckBox, QDialog,
                            QTabWidget, QGroupBox, QDialogButtonBox, QComboBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPalette, QColor, QAction
from file_encryptor import SecureFileEncryptor
import json
import gettext
import subprocess

_ = gettext.gettext  # Define the translation function

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
    
    OPACITY_LEVELS = {
        'Full': 1.0,
        'Slight': 0.95,
        'Medium': 0.9,
        'High': 0.8
    }

class EncryptionThread(QThread):
    """Background thread for encryption/decryption operations."""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, mode: str, input_path: str, output_path: str, 
                 passphrase: str, delete_original: bool):
        super().__init__()
        self.mode = mode
        self.input_path = input_path
        self.output_path = output_path
        self.passphrase = passphrase
        self.delete_original = delete_original
        
    def run(self):
        try:
            # Check if input file exists and is readable
            if not os.path.exists(self.input_path):
                raise FileNotFoundError(f"Input file not found: {self.input_path}")
            if not os.access(self.input_path, os.R_OK):
                raise PermissionError(f"Cannot read input file: {self.input_path}")
                
            # Check if output directory is writable
            output_dir = os.path.dirname(self.output_path) or '.'
            if not os.access(output_dir, os.W_OK):
                raise PermissionError(f"Cannot write to output directory: {output_dir}")
            
            encryptor = SecureFileEncryptor()
            if self.mode == 'encrypt':
                encryptor.encrypt_file(self.input_path, self.output_path, 
                                     self.passphrase, self.delete_original)
            else:
                encryptor.decrypt_file(self.input_path, self.output_path, 
                                     self.passphrase)
            self.finished.emit(True, "Operation completed successfully!")
        except Exception as e:
            self.finished.emit(False, str(e))

class LanguageManager:
    """Manage application languages"""
    
    LANGUAGES = {
        'English (US)': 'en_US',
        'English (UK)': 'en_GB',
        'Turkish': 'tr_TR',
        'German': 'de_DE',
        'Russian': 'ru_RU',
        'French': 'fr_FR',
        'Spanish': 'es_ES'
    }

    LANGUAGE_FLAGS = {
        'English (US)': '🇺🇸',
        'English (UK)': '🇬🇧',
        'Turkish': '🇹🇷',
        'German': '🇩🇪',
        'Russian': '🇷🇺',
        'French': '🇫🇷',
        'Spanish': '🇪🇸'
    }
    
    def __init__(self):
        self.current_lang = 'en_US'
        self.translations = {}
        self._load_translations()
    
    def _load_translations(self):
        """Load all language translations"""
        for lang_code in self.LANGUAGES.values():
            try:
                translation = gettext.translation(
                    'solacecrypt',
                    localedir='/usr/local/share/solacecrypt/locale',
                    languages=[lang_code]
                )
                self.translations[lang_code] = translation
            except FileNotFoundError:
                # Fallback to default English strings
                self.translations[lang_code] = gettext.NullTranslations()
    
    def set_language(self, lang_name: str):
        """Set the current language"""
        lang_code = self.LANGUAGES.get(lang_name, 'en_US')
        self.current_lang = lang_code
        self.translations[lang_code].install()

class Settings:
    """Manage application settings"""
    
    DEFAULT_SETTINGS = {
        'theme': 'Dark Blue',
        'button_style': 'Rounded',
        'language': 'English (US)',
        'auto_clear': True,
        'confirm_delete': True,
        'show_notifications': True,
        'opacity': 'Full'
    }
    
    def __init__(self):
        self.settings_file = Path.home() / '.config' / 'solacecrypt' / 'settings.json'
        self.settings = self.load_settings()
    
    def load_settings(self) -> dict:
        """Load settings from file or create default"""
        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    return {**self.DEFAULT_SETTINGS, **json.load(f)}
            return self.DEFAULT_SETTINGS.copy()
        except Exception:
            return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

class SettingsDialog(QDialog):
    """Settings dialog window"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        """Initialize settings dialog UI"""
        self.setWindowTitle(_('Settings'))
        self.setMinimumWidth(500)
        layout = QVBoxLayout(self)
        
        # Create tabs
        tabs = QTabWidget()
        
        # Appearance tab
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout(appearance_tab)
        
        # Theme selection
        theme_group = QGroupBox(_('Theme'))
        theme_layout = QVBoxLayout(theme_group)
        
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(ThemeManager.THEMES.keys())
        self.theme_selector.setCurrentText(self.parent.settings.settings['theme'])
        theme_layout.addWidget(self.theme_selector)
        
        # Transparency selection
        transparency_group = QGroupBox(_('Window Transparency'))
        transparency_layout = QVBoxLayout(transparency_group)
        
        self.transparency_selector = QComboBox()
        self.transparency_selector.addItems(ThemeManager.OPACITY_LEVELS.keys())
        self.transparency_selector.setCurrentText(self.parent.settings.settings['opacity'])
        transparency_layout.addWidget(self.transparency_selector)
        
        appearance_layout.addWidget(theme_group)
        
        # Button style selection
        button_style_group = QGroupBox(_('Button Style'))
        button_style_layout = QVBoxLayout(button_style_group)
        
        self.button_style_selector = QComboBox()
        self.button_style_selector.addItems(ThemeManager.BUTTON_STYLES.keys())
        self.button_style_selector.setCurrentText(self.parent.settings.settings['button_style'])
        button_style_layout.addWidget(self.button_style_selector)
        
        appearance_layout.addWidget(button_style_group)
        
        # Language tab
        language_tab = QWidget()
        language_layout = QVBoxLayout(language_tab)
        
        language_group = QGroupBox(_('Language'))
        language_group_layout = QVBoxLayout(language_group)
        
        self.language_selector = QComboBox()
        for lang_name in LanguageManager.LANGUAGES.keys():
            self.language_selector.addItem(
                f"{LanguageManager.LANGUAGE_FLAGS[lang_name]} {lang_name}"
            )
        current_lang = self.parent.settings.settings['language']
        self.language_selector.setCurrentText(
            f"{LanguageManager.LANGUAGE_FLAGS[current_lang]} {current_lang}"
        )
        language_group_layout.addWidget(self.language_selector)
        
        language_layout.addWidget(language_group)
        
        # Behavior tab
        behavior_tab = QWidget()
        behavior_layout = QVBoxLayout(behavior_tab)
        
        # Auto-clear option
        self.auto_clear = QCheckBox(_('Automatically clear inputs after operation'))
        self.auto_clear.setChecked(self.parent.settings.settings['auto_clear'])
        behavior_layout.addWidget(self.auto_clear)
        
        # Confirm delete option
        self.confirm_delete = QCheckBox(_('Confirm before deleting files'))
        self.confirm_delete.setChecked(self.parent.settings.settings['confirm_delete'])
        behavior_layout.addWidget(self.confirm_delete)
        
        # Show notifications option
        self.show_notifications = QCheckBox(_('Show desktop notifications'))
        self.show_notifications.setChecked(self.parent.settings.settings['show_notifications'])
        behavior_layout.addWidget(self.show_notifications)
        
        # Add tabs
        tabs.addTab(appearance_tab, _('Appearance'))
        tabs.addTab(language_tab, _('Language'))
        tabs.addTab(behavior_tab, _('Behavior'))
        
        layout.addWidget(tabs)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def accept(self):
        """Save settings when OK is clicked"""
        self.parent.settings.settings.update({
            'theme': self.theme_selector.currentText(),
            'button_style': self.button_style_selector.currentText(),
            'language': self.language_selector.currentText().split(' ')[1],
            'auto_clear': self.auto_clear.isChecked(),
            'confirm_delete': self.confirm_delete.isChecked(),
            'show_notifications': self.show_notifications.isChecked(),
            'opacity': self.transparency_selector.currentText(),
        })
        self.parent.settings.save_settings()
        self.parent.apply_settings()
        super().accept()

class FileManager:
    """Manage encrypted files and folders"""
    
    def __init__(self):
        self.encrypted_folder = Path.home() / 'Encrypted'
        self.create_encrypted_folder()
    
    def create_encrypted_folder(self):
        """Create the encrypted files folder if it doesn't exist"""
        self.encrypted_folder.mkdir(exist_ok=True)
    
    def hide_folder(self):
        """Hide the encrypted folder"""
        try:
            # Create a .hidden file in home directory
            hidden_file = Path.home() / '.hidden'
            if not hidden_file.exists():
                hidden_file.touch()
            
            # Add 'Encrypted' to .hidden file if not already there
            content = hidden_file.read_text().splitlines()
            if 'Encrypted' not in content:
                with hidden_file.open('a') as f:
                    f.write('Encrypted\n')
            
            # Also set the hidden attribute
            subprocess.run(['attrib', '+h', str(self.encrypted_folder)], 
                         check=True, capture_output=True)
            return True
        except Exception as e:
            print(f"Error hiding folder: {e}")
            return False
    
    def unhide_folder(self):
        """Unhide the encrypted folder"""
        try:
            # Remove from .hidden file
            hidden_file = Path.home() / '.hidden'
            if hidden_file.exists():
                content = hidden_file.read_text().splitlines()
                content = [line for line in content if line != 'Encrypted']
                hidden_file.write_text('\n'.join(content))
            
            # Remove hidden attribute
            subprocess.run(['attrib', '-h', str(self.encrypted_folder)], 
                         check=True, capture_output=True)
            return True
        except Exception as e:
            print(f"Error unhiding folder: {e}")
            return False
    
    def get_output_path(self, input_path: str, mode: str) -> Path:
        """Generate output path in encrypted folder"""
        input_file = Path(input_path)
        if mode == 'encrypt':
            return self.encrypted_folder / f"{input_file.stem}.enc"
        else:
            return self.encrypted_folder / input_file.stem

class FileEncryptorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SolaceCrypt')  # Set window title
        self.setObjectName('SolaceCrypt')   # Set object name for window manager
        self.settings = Settings()
        self.lang_manager = LanguageManager()
        self.file_manager = FileManager()  # Add file manager
        self.lang_manager.set_language(self.settings.settings['language'])
        self.thread = None
        self.init_ui()
        self.apply_settings()
        
    def init_ui(self):
        """Initialize the user interface with improved layout and styling."""
        self.setMinimumWidth(700)
        self.setMinimumHeight(400)
        
        # Create menu bar first
        self.create_menu_bar()
        
        # Create main layout with proper spacing
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
        layout.addWidget(header)
        
        # File selection section
        file_group = QWidget()
        file_layout = QHBoxLayout(file_group)
        
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText('Select a file to encrypt/decrypt...')
        self.file_path.setReadOnly(True)
        
        browse_btn = QPushButton('Browse')
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self.browse_file)
        
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(browse_btn)
        layout.addWidget(file_group)
        
        # Output path selection
        output_group = QWidget()
        output_layout = QHBoxLayout(output_group)
        
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText('Select output location...')
        self.output_path.setReadOnly(True)
        
        browse_output_btn = QPushButton('Browse')
        browse_output_btn.setFixedWidth(100)
        browse_output_btn.clicked.connect(self.browse_output)
        
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(browse_output_btn)
        layout.addWidget(output_group)
        
        # Checkbox group
        checkbox_group = QWidget()
        checkbox_layout = QVBoxLayout(checkbox_group)
        
        # Show passphrase checkbox
        self.show_pass = QCheckBox('Show passphrase')
        self.show_pass.stateChanged.connect(self.toggle_passphrase_visibility)
        checkbox_layout.addWidget(self.show_pass)
        
        # Hide encrypted folder checkbox
        self.hide_folder = QCheckBox('Hide encrypted folder')
        self.hide_folder.stateChanged.connect(self.toggle_folder_visibility)
        checkbox_layout.addWidget(self.hide_folder)
        
        # Delete original file checkbox
        self.delete_original = QCheckBox('Securely delete original file')
        checkbox_layout.addWidget(self.delete_original)
        
        layout.addWidget(checkbox_group)
        
        # Passphrase section
        pass_group = QWidget()
        pass_layout = QVBoxLayout(pass_group)
        
        self.passphrase = QLineEdit()
        self.passphrase.setPlaceholderText('Enter passphrase')
        self.passphrase.setEchoMode(QLineEdit.EchoMode.Password)
        
        pass_layout.addWidget(self.passphrase)
        layout.addWidget(pass_group)
        
        # Action buttons
        btn_group = QWidget()
        btn_layout = QHBoxLayout(btn_group)
        
        self.encrypt_btn = QPushButton('Encrypt')
        self.encrypt_btn.clicked.connect(lambda: self.process_file('encrypt'))
        
        self.decrypt_btn = QPushButton('Decrypt')
        self.decrypt_btn.clicked.connect(lambda: self.process_file('decrypt'))
        
        btn_layout.addWidget(self.encrypt_btn)
        btn_layout.addWidget(self.decrypt_btn)
        layout.addWidget(btn_group)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Set dark theme by default
        self.set_dark_theme()
        
    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu(_('File'))
        
        # Remove folder visibility actions and just add exit
        exit_action = QAction(_('Exit'), self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu (single menu for all settings)
        settings_menu = menubar.addMenu(_('Settings'))
        
        # General settings
        settings_action = QAction(_('Preferences'), self)
        settings_action.setShortcut('Ctrl+,')
        settings_action.triggered.connect(self.show_settings)
        settings_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu(_('Help'))
        
        about_action = QAction(_('About SolaceCrypt'), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def set_dark_theme(self):
        """Apply a modern dark theme to the application."""
        palette = QPalette()
        
        # Define colors
        background = QColor("#2E2E2E")
        foreground = QColor("#E0E0E0")
        accent = QColor("#0D47A1")  # Deep blue
        secondary = QColor("#424242")
        
        # Set colors for different UI elements
        palette.setColor(QPalette.ColorRole.Window, background)
        palette.setColor(QPalette.ColorRole.WindowText, foreground)
        palette.setColor(QPalette.ColorRole.Base, QColor("#1E1E1E"))
        palette.setColor(QPalette.ColorRole.AlternateBase, secondary)
        palette.setColor(QPalette.ColorRole.ToolTipBase, background)
        palette.setColor(QPalette.ColorRole.ToolTipText, foreground)
        palette.setColor(QPalette.ColorRole.Text, foreground)
        palette.setColor(QPalette.ColorRole.Button, secondary)
        palette.setColor(QPalette.ColorRole.ButtonText, foreground)
        palette.setColor(QPalette.ColorRole.Link, accent)
        palette.setColor(QPalette.ColorRole.Highlight, accent)
        palette.setColor(QPalette.ColorRole.HighlightedText, foreground)
        
        QApplication.instance().setPalette(palette)
        
        # Additional styling
        style = """
            QPushButton {
                background-color: #0D47A1;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton:pressed {
                background-color: #0A367A;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #424242;
                border-radius: 4px;
                background-color: #1E1E1E;
            }
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #424242;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0D47A1;
                border-radius: 4px;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """
        QApplication.instance().setStyleSheet(style)
        
    def set_light_theme(self):
        """Apply light theme to the application."""
        QApplication.instance().setPalette(QApplication.style().standardPalette())
        
    def browse_file(self):
        """Open file dialog to select a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            str(Path.home()),
            "All Files (*.*)"
        )
        if file_path:
            self.file_path.setText(file_path)
            
    def browse_output(self):
        """Open dialog to select output location."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Output Location",
            str(Path.home()),
            QFileDialog.Option.ShowDirsOnly
        )
        if folder_path:
            self.output_path.setText(folder_path)
        
    def toggle_passphrase_visibility(self, state):
        """Toggle passphrase visibility."""
        self.passphrase.setEchoMode(
            QLineEdit.EchoMode.Normal if state 
            else QLineEdit.EchoMode.Password
        )
        
    def toggle_folder_visibility(self, state):
        """Toggle encrypted folder visibility."""
        try:
            if state:
                reply = QMessageBox.question(
                    self,
                    'Hide Encrypted Folder',
                    'Do you want to hide the encrypted folder?\n\n'
                    'The folder will be hidden from file managers but still accessible.',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    if self.file_manager.hide_folder():
                        self.status_bar.showMessage("Encrypted folder hidden")
                    else:
                        self.status_bar.showMessage("Failed to hide folder")
                        self.hide_folder.setChecked(False)
                else:
                    self.hide_folder.setChecked(False)
            else:
                if self.file_manager.unhide_folder():
                    self.status_bar.showMessage("Encrypted folder visible")
                else:
                    self.status_bar.showMessage("Failed to show folder")
                    self.hide_folder.setChecked(True)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to change folder visibility: {str(e)}")
            self.hide_folder.setChecked(not state)
        
    def process_file(self, mode):
        """Start the encryption/decryption process."""
        if not self.file_path.text():
            QMessageBox.warning(self, "Error", "Please select a file first!")
            return
            
        if not self.passphrase.text():
            QMessageBox.warning(self, "Error", "Please enter a passphrase!")
            return
            
        input_path = self.file_path.text()
        
        # Use custom output path if specified, otherwise use default location
        if self.output_path.text():
            base_path = self.output_path.text()
            filename = Path(input_path).name
            if mode == 'encrypt':
                output_path = str(Path(base_path) / f"{Path(filename).stem}.enc")
            else:
                output_path = str(Path(base_path) / Path(filename).stem)
        else:
            # Use default encrypted folder
            output_path = str(self.file_manager.get_output_path(input_path, mode))
        
        # Check if output file already exists
        if os.path.exists(output_path):
            reply = QMessageBox.question(
                self,
                'File exists',
                f'The output file already exists.\nDo you want to overwrite it?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Cleanup previous thread if exists
        if self.thread is not None and self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()
            
        # Start the encryption/decryption thread
        self.thread = EncryptionThread(
            mode, input_path, output_path,
            self.passphrase.text(),
            self.delete_original.isChecked()
        )
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.process_completed)
        
        # Disable UI elements
        self.encrypt_btn.setEnabled(False)
        self.decrypt_btn.setEnabled(False)
        self.file_path.setEnabled(False)
        self.passphrase.setEnabled(False)
        self.delete_original.setEnabled(False)
        self.show_pass.setEnabled(False)
        self.hide_folder.setEnabled(False)
        
        # Show progress bar
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)  # Infinite progress bar
        self.status_bar.showMessage(f"{'Encrypting' if mode == 'encrypt' else 'Decrypting'} file...")
        
        self.thread.start()
        
    def update_progress(self, value):
        """Update the progress bar."""
        self.progress.setValue(value)
        
    def process_completed(self, success, message):
        """Handle process completion."""
        self.progress.setVisible(False)
        self.status_bar.clearMessage()
        
        # Re-enable UI elements
        self.encrypt_btn.setEnabled(True)
        self.decrypt_btn.setEnabled(True)
        self.file_path.setEnabled(True)
        self.passphrase.setEnabled(True)
        self.delete_original.setEnabled(True)
        self.show_pass.setEnabled(True)
        self.hide_folder.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.file_path.clear()
            self.passphrase.clear()
            self.delete_original.setChecked(False)
        else:
            QMessageBox.critical(self, "Error", message)
            
    def closeEvent(self, event):
        """Handle application closing."""
        if self.thread is not None and self.thread.isRunning():
            reply = QMessageBox.question(self, 'Confirm Exit',
                                       'An operation is in progress. Are you sure you want to quit?',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.thread.terminate()
                self.thread.wait()
            else:
                event.ignore()
                return
        event.accept()

    def show_settings(self):
        """Show the settings dialog"""
        dialog = SettingsDialog(self)
        dialog.exec()

    def apply_settings(self):
        """Apply current settings"""
        try:
            # Apply theme
            self.change_theme(self.settings.settings['theme'])
            
            # Apply opacity
            opacity = ThemeManager.OPACITY_LEVELS[self.settings.settings['opacity']]
            self.setWindowOpacity(opacity)
            
            # Apply language (save current language before changing)
            current_lang = self.settings.settings['language']
            self.lang_manager.set_language(current_lang)
            
            # Update UI text without recreating the window
            self.retranslate_ui()
            
            # Save settings
            self.settings.save_settings()
            
        except Exception as e:
            QMessageBox.warning(self, "Settings Error", f"Failed to apply settings: {str(e)}")
            # Revert to previous language if there's an error
            self.settings.settings['language'] = current_lang

    def retranslate_ui(self):
        """Update all UI text for current language"""
        try:
            # Update window title
            self.setWindowTitle('SolaceCrypt')
            
            # Update menu items
            self.update_menu_text()
            
            # Update labels and buttons
            self.update_ui_elements()
            
        except Exception as e:
            print(f"Translation error: {e}")

    def update_menu_text(self):
        """Update menu text with current language"""
        file_menu = self.menuBar().findChild(QMenu, "file_menu")
        if file_menu:
            file_menu.setTitle(_('File'))
        
        settings_menu = self.menuBar().findChild(QMenu, "settings_menu")
        if settings_menu:
            settings_menu.setTitle(_('Settings'))

    def update_ui_elements(self):
        """Update UI elements with current language"""
        # Update buttons
        self.encrypt_btn.setText(_('Encrypt'))
        self.decrypt_btn.setText(_('Decrypt'))
        
        # Update checkboxes
        self.show_pass.setText(_('Show passphrase'))
        self.hide_folder.setText(_('Hide encrypted folder'))
        self.delete_original.setText(_('Securely delete original file'))
        
        # Update placeholders
        self.file_path.setPlaceholderText(_('Select a file to encrypt/decrypt...'))
        self.passphrase.setPlaceholderText(_('Enter passphrase'))

    def change_theme(self, theme_name):
        """Apply selected theme to the application."""
        theme = ThemeManager.THEMES[theme_name]
        
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
                border-radius: {ThemeManager.BUTTON_STYLES[self.settings.settings['button_style']]};
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

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About SolaceCrypt",
            """
            <h2>SolaceCrypt</h2>
            <p>Version 1.0</p>
            <p>A secure file encryption tool.</p>
            <p>© 2024 SolaceCrypt</p>
            """
        )

def main():
    app = QApplication(sys.argv)
    
    # Set application-wide stylesheet
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = FileEncryptorGUI()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 