#!/bin/bash

# Create messages.pot template
xgettext -d solacecrypt -o messages.pot file_encryptor_gui.py

# Create translation directories
for lang in en_US en_GB tr_TR de_DE ru_RU; do
    mkdir -p locale/$lang/LC_MESSAGES
    msginit -i messages.pot -o locale/$lang/LC_MESSAGES/solacecrypt.po -l $lang
done

# Compile translations
for lang in en_US en_GB tr_TR de_DE ru_RU; do
    msgfmt locale/$lang/LC_MESSAGES/solacecrypt.po -o locale/$lang/LC_MESSAGES/solacecrypt.mo
done 