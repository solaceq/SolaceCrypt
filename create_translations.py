#!/usr/bin/env python3

import os
import json

TRANSLATIONS = {
    'tr_TR': {
        'File': 'Dosya',
        'Settings': 'Ayarlar',
        'Help': 'Yardım',
        'Exit': 'Çıkış',
        'Preferences': 'Tercihler',
        'Window Transparency': 'Pencere Şeffaflığı',
        'About SolaceCrypt': 'SolaceCrypt Hakkında',
        'Select File': 'Dosya Seç',
        'Select Output Location': 'Çıktı Konumunu Seç',
        'Show passphrase': 'Parolayı Göster',
        'Hide encrypted folder': 'Şifreli Klasörü Gizle',
        'Securely delete original file': 'Orijinal Dosyayı Güvenli Şekilde Sil',
        'Enter passphrase': 'Parola Girin',
        'Encrypt': 'Şifrele',
        'Decrypt': 'Şifre Çöz',
        'Theme': 'Tema',
        'Language': 'Dil',
        'Button Style': 'Düğme Stili',
        'Appearance': 'Görünüm',
        'Behavior': 'Davranış',
        'Operation completed successfully!': 'İşlem başarıyla tamamlandı!',
        'Please select a file first!': 'Lütfen önce bir dosya seçin!',
        'Please enter a passphrase!': 'Lütfen bir parola girin!',
        'File exists': 'Dosya mevcut',
        'Success': 'Başarılı',
        'Error': 'Hata',
        'Confirm Exit': 'Çıkışı Onayla',
        'Version': 'Sürüm'
    },
    'de_DE': {
        'File': 'Datei',
        'Settings': 'Einstellungen',
        'Help': 'Hilfe',
        'Exit': 'Beenden',
        'Preferences': 'Einstellungen',
        'Window Transparency': 'Fenstertransparenz',
        'About SolaceCrypt': 'Über SolaceCrypt',
        'Select File': 'Datei auswählen',
        'Select Output Location': 'Ausgabeort wählen',
        'Show passphrase': 'Passphrase anzeigen',
        'Hide encrypted folder': 'Verschlüsselten Ordner ausblenden',
        'Securely delete original file': 'Originaldatei sicher löschen',
        'Enter passphrase': 'Passphrase eingeben',
        'Encrypt': 'Verschlüsseln',
        'Decrypt': 'Entschlüsseln',
        'Theme': 'Thema',
        'Language': 'Sprache',
        'Button Style': 'Schaltflächenstil',
        'Appearance': 'Aussehen',
        'Behavior': 'Verhalten',
        'Operation completed successfully!': 'Vorgang erfolgreich abgeschlossen!',
        'Please select a file first!': 'Bitte wählen Sie zuerst eine Datei aus!',
        'Please enter a passphrase!': 'Bitte geben Sie eine Passphrase ein!',
        'File exists': 'Datei existiert bereits',
        'Success': 'Erfolg',
        'Error': 'Fehler',
        'Confirm Exit': 'Beenden bestätigen',
        'Version': 'Version'
    },
    'ru_RU': {
        'File': 'Файл',
        'Settings': 'Настройки',
        'Help': 'Помощь',
        'Exit': 'Выход',
        'Preferences': 'Параметры',
        'Window Transparency': 'Прозрачность окна',
        'About SolaceCrypt': 'О SolaceCrypt',
        'Select File': 'Выбрать файл',
        'Select Output Location': 'Выбрать место сохранения',
        'Show passphrase': 'Показать пароль',
        'Hide encrypted folder': 'Скрыть зашифрованную папку',
        'Securely delete original file': 'Безопасно удалить исходный файл',
        'Enter passphrase': 'Введите пароль',
        'Encrypt': 'Зашифровать',
        'Decrypt': 'Расшифровать',
        'Theme': 'Тема',
        'Language': 'Язык',
        'Button Style': 'Стиль кнопок',
        'Appearance': 'Внешний вид',
        'Behavior': 'Поведение',
        'Operation completed successfully!': 'Операция успешно завершена!',
        'Please select a file first!': 'Пожалуйста, сначала выберите файл!',
        'Please enter a passphrase!': 'Пожалуйста, введите пароль!',
        'File exists': 'Файл существует',
        'Success': 'Успех',
        'Error': 'Ошибка',
        'Confirm Exit': 'Подтвердить выход',
        'Version': 'Версия'
    },
    'fr_FR': {
        'File': 'Fichier',
        'Settings': 'Paramètres',
        'Help': 'Aide',
        'Exit': 'Quitter',
        'Preferences': 'Préférences',
        'Window Transparency': 'Transparence de la fenêtre',
        'About SolaceCrypt': 'À propos de SolaceCrypt',
        'Select File': 'Sélectionner un fichier',
        'Select Output Location': 'Sélectionner l\'emplacement de sortie',
        'Show passphrase': 'Afficher le mot de passe',
        'Hide encrypted folder': 'Masquer le dossier chiffré',
        'Securely delete original file': 'Supprimer le fichier original en toute sécurité',
        'Enter passphrase': 'Entrer le mot de passe',
        'Encrypt': 'Chiffrer',
        'Decrypt': 'Déchiffrer',
        'Theme': 'Thème',
        'Language': 'Langue',
        'Button Style': 'Style des boutons',
        'Appearance': 'Apparence',
        'Behavior': 'Comportement',
        'Operation completed successfully!': 'Opération terminée avec succès !',
        'Please select a file first!': 'Veuillez d\'abord sélectionner un fichier !',
        'Please enter a passphrase!': 'Veuillez entrer un mot de passe !',
        'File exists': 'Le fichier existe',
        'Success': 'Succès',
        'Error': 'Erreur',
        'Confirm Exit': 'Confirmer la sortie',
        'Version': 'Version'
    },
    'es_ES': {
        'File': 'Archivo',
        'Settings': 'Configuración',
        'Help': 'Ayuda',
        'Exit': 'Salir',
        'Preferences': 'Preferencias',
        'Window Transparency': 'Transparencia de ventana',
        'About SolaceCrypt': 'Acerca de SolaceCrypt',
        'Select File': 'Seleccionar archivo',
        'Select Output Location': 'Seleccionar ubicación de salida',
        'Show passphrase': 'Mostrar contraseña',
        'Hide encrypted folder': 'Ocultar carpeta cifrada',
        'Securely delete original file': 'Eliminar archivo original de forma segura',
        'Enter passphrase': 'Introducir contraseña',
        'Encrypt': 'Cifrar',
        'Decrypt': 'Descifrar',
        'Theme': 'Tema',
        'Language': 'Idioma',
        'Button Style': 'Estilo de botones',
        'Appearance': 'Apariencia',
        'Behavior': 'Comportamiento',
        'Operation completed successfully!': '¡Operación completada con éxito!',
        'Please select a file first!': '¡Por favor, seleccione primero un archivo!',
        'Please enter a passphrase!': '¡Por favor, introduzca una contraseña!',
        'File exists': 'El archivo existe',
        'Success': 'Éxito',
        'Error': 'Error',
        'Confirm Exit': 'Confirmar salida',
        'Version': 'Versión'
    }
}

def create_translation_files():
    base_dir = 'locale'
    
    for lang_code, translations in TRANSLATIONS.items():
        # Create language directory
        lang_dir = os.path.join(base_dir, lang_code, 'LC_MESSAGES')
        os.makedirs(lang_dir, exist_ok=True)
        
        # Create .po file
        po_file = os.path.join(lang_dir, 'solacecrypt.po')
        with open(po_file, 'w', encoding='utf-8') as f:
            f.write('msgid ""\n')
            f.write('msgstr ""\n\n')
            
            for msgid, msgstr in translations.items():
                f.write(f'msgid "{msgid}"\n')
                f.write(f'msgstr "{msgstr}"\n\n')
        
        # Compile to .mo file
        os.system(f'msgfmt {po_file} -o {os.path.join(lang_dir, "solacecrypt.mo")}')

if __name__ == '__main__':
    create_translation_files() 