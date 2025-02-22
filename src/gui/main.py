from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import Qt
import sys
import os
from pathlib import Path
from ctypes import cdll
from file_encryptor_gui import FileEncryptorGUI

# Import extension wrappers
from extensions.rust_wrapper import RustEncryption
from extensions.nim_wrapper import NimHandler
from extensions.julia_wrapper import JuliaHandler

class EnhancedFileEncryptorGUI(FileEncryptorGUI):
    def __init__(self):
        super().__init__()
        self.init_enhanced_features()

    def init_enhanced_features(self):
        """Initialize additional features from other languages"""
        # Initialize Rust components
        self.rust = RustEncryption()
        if self.rust.available:
            self.rust_encryptor = self.rust.encryptor

        # Initialize Nim components
        self.nim = NimHandler()
        if self.nim.available:
            self.file_handler = self.nim.handler

        # Initialize other components with try/except
        try:
            self.secure_mem = cdll.LoadLibrary("./libsecure_mem.so")
        except OSError:
            self.secure_mem = None

        # Initialize Julia components
        self.julia_handler = JuliaHandler()
        if self.julia_handler.available:
            self.julia = self.julia_handler.julia
            self.crypto = self.julia_handler.crypto

        # Add more components as needed

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = EnhancedFileEncryptorGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 