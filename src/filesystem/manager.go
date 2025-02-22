package filesystem

import (
    "os"
    "path/filepath"
    "fmt"
    "strings"
)

type FileManager struct {
    EncryptedDir string
}

func NewFileManager(homeDir string) *FileManager {
    return &FileManager{
        EncryptedDir: filepath.Join(homeDir, "Encrypted"),
    }
}

func (fm *FileManager) HideFolder() error {
    // Linux-specific folder hiding
    hiddenFile := filepath.Join(os.Getenv("HOME"), ".hidden")
    
    if _, err := os.Stat(hiddenFile); os.IsNotExist(err) {
        if _, err := os.Create(hiddenFile); err != nil {
            return fmt.Errorf("failed to create .hidden file: %v", err)
        }
    }
    
    content, err := os.ReadFile(hiddenFile)
    if err != nil {
        return fmt.Errorf("failed to read .hidden file: %v", err)
    }
    
    if !strings.Contains(string(content), "Encrypted\n") {
        f, err := os.OpenFile(hiddenFile, os.O_APPEND|os.O_WRONLY, 0600)
        if err != nil {
            return fmt.Errorf("failed to open .hidden file: %v", err)
        }
        defer f.Close()
        
        if _, err := f.WriteString("Encrypted\n"); err != nil {
            return fmt.Errorf("failed to write to .hidden file: %v", err)
        }
    }
    
    return nil
} 