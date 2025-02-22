#!/usr/bin/env python3
import sys
from PyQt6.QtWidgets import (QApplication, QWizard, QWizardPage, QLabel, 
                            QVBoxLayout, QCheckBox, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import subprocess
import os

class InstallationThread(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, options):
        super().__init__()
        self.options = options
        
    def run(self):
        try:
            # Run installation script
            process = subprocess.Popen(
                ['sudo', './install.sh'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            while True:
                output = process.stdout.readline()
                if output == b'' and process.poll() is not None:
                    break
                if output:
                    self.progress.emit(50, output.decode().strip())
                    
            if process.returncode == 0:
                self.finished.emit(True, "Installation completed successfully!")
            else:
                self.finished.emit(False, "Installation failed!")
        except Exception as e:
            self.finished.emit(False, str(e))

class InstallWizard(QWizard):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SolaceCrypt Installer")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        
        self.addPage(WelcomePage())
        self.addPage(OptionsPage())
        self.addPage(InstallPage())
        
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

class WelcomePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Welcome to SolaceCrypt Installer")
        
        layout = QVBoxLayout()
        label = QLabel(
            "This wizard will guide you through the installation of SolaceCrypt.\n\n"
            "SolaceCrypt is a secure file encryption tool that helps protect your "
            "sensitive files using strong encryption."
        )
        label.setWordWrap(True)
        layout.addWidget(label)
        self.setLayout(layout)

class OptionsPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Installation Options")
        
        layout = QVBoxLayout()
        
        self.create_desktop = QCheckBox("Create desktop shortcut")
        self.create_desktop.setChecked(True)
        
        self.add_path = QCheckBox("Add to system PATH")
        self.add_path.setChecked(True)
        
        self.install_deps = QCheckBox("Install dependencies")
        self.install_deps.setChecked(True)
        
        layout.addWidget(self.create_desktop)
        layout.addWidget(self.add_path)
        layout.addWidget(self.install_deps)
        
        self.setLayout(layout)

class InstallPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Installing SolaceCrypt")
        
        layout = QVBoxLayout()
        
        self.status = QLabel("Installation in progress...")
        self.progress = QProgressBar()
        
        layout.addWidget(self.status)
        layout.addWidget(self.progress)
        
        self.setLayout(layout)
        
    def initializePage(self):
        self.thread = InstallationThread({
            'desktop': self.wizard().page(1).create_desktop.isChecked(),
            'path': self.wizard().page(1).add_path.isChecked(),
            'deps': self.wizard().page(1).install_deps.isChecked()
        })
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.installation_finished)
        self.thread.start()
        
    def update_progress(self, value, message):
        self.progress.setValue(value)
        self.status.setText(message)
        
    def installation_finished(self, success, message):
        if success:
            self.wizard().next()
        else:
            self.status.setText(f"Installation failed: {message}")

def main():
    app = QApplication(sys.argv)
    wizard = InstallWizard()
    wizard.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 