#!/usr/bin/env python3

import os
import sys
import argparse
import secrets
from pathlib import Path
from typing import Optional
import shutil

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from tqdm import tqdm

class SecureFileEncryptor:
    SALT_SIZE = 16
    NONCE_SIZE = 12
    CHUNK_SIZE = 64 * 1024  # 64KB chunks for reading large files
    
    def __init__(self):
        self.salt = None
        self.key = None
        
    def _derive_key(self, passphrase: str, salt: Optional[bytes] = None) -> bytes:
        """Derive encryption key from passphrase using PBKDF2."""
        if salt is None:
            salt = secrets.token_bytes(self.SALT_SIZE)
        self.salt = salt
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256-bit key
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(passphrase.encode())
    
    def _secure_wipe(self, *args):
        """Securely wipe sensitive data from memory."""
        for arg in args:
            if isinstance(arg, bytes):
                # Create a new bytes object filled with zeros
                # instead of trying to modify the original
                arg = bytes(0 for _ in range(len(arg)))
            elif isinstance(arg, str):
                del arg
                
    def encrypt_file(self, input_path: str, output_path: str, passphrase: str, 
                     delete_original: bool = False) -> None:
        """
        Encrypt a file using AES-256-GCM.
        
        Args:
            input_path: Path to the file to encrypt
            output_path: Path where to save the encrypted file
            passphrase: Password to use for encryption
            delete_original: Whether to securely delete the original file
        """
        try:
            # Generate key and nonce
            key = self._derive_key(passphrase)
            nonce = secrets.token_bytes(self.NONCE_SIZE)
            aesgcm = AESGCM(key)
            
            # Read file in chunks to handle large files
            chunks = []
            total_size = os.path.getsize(input_path)
            
            with open(input_path, 'rb') as in_file:
                while True:
                    chunk = in_file.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    chunks.append(chunk)
            
            # Concatenate all chunks and encrypt at once
            data = b''.join(chunks)
            encrypted_data = aesgcm.encrypt(nonce, data, None)
            
            # Write encrypted data with salt and nonce
            with open(output_path, 'wb') as out_file:
                # Write metadata
                out_file.write(self.salt)  # First 16 bytes: salt
                out_file.write(nonce)      # Next 12 bytes: nonce
                # Write encrypted data
                out_file.write(encrypted_data)
            
            if delete_original:
                self._secure_delete_file(input_path)
                
        finally:
            self._secure_wipe(key, passphrase)
            
    def decrypt_file(self, input_path: str, output_path: str, passphrase: str) -> None:
        """
        Decrypt a file using AES-256-GCM.
        
        Args:
            input_path: Path to the encrypted file
            output_path: Path where to save the decrypted file
            passphrase: Password used for encryption
        
        Raises:
            ValueError: If password is incorrect or file is corrupted
        """
        try:
            with open(input_path, 'rb') as in_file:
                # Read metadata
                salt = in_file.read(self.SALT_SIZE)
                if len(salt) != self.SALT_SIZE:
                    raise ValueError("Invalid encrypted file: missing salt")
                
                nonce = in_file.read(self.NONCE_SIZE)
                if len(nonce) != self.NONCE_SIZE:
                    raise ValueError("Invalid encrypted file: missing nonce")
                
                # Read encrypted data
                encrypted_data = in_file.read()
                if not encrypted_data:
                    raise ValueError("Invalid encrypted file: no encrypted data")
                
                # Derive key using the same salt
                key = self._derive_key(passphrase, salt)
                aesgcm = AESGCM(key)
                
                try:
                    # Decrypt data
                    decrypted_data = aesgcm.decrypt(nonce, encrypted_data, None)
                except InvalidTag:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    raise ValueError("Decryption failed: Wrong password")
                
                # Write decrypted data
                with open(output_path, 'wb') as out_file:
                    out_file.write(decrypted_data)
                
        finally:
            self._secure_wipe(key, passphrase)
            
    def _secure_delete_file(self, file_path: str) -> None:
        """Securely delete a file by overwriting with random data before deletion."""
        file_size = os.path.getsize(file_path)
        with open(file_path, 'wb') as f:
            for _ in range(3):  # Overwrite 3 times
                f.seek(0)
                f.write(secrets.token_bytes(file_size))
                f.flush()
                os.fsync(f.fileno())
        os.remove(file_path)

def main():
    parser = argparse.ArgumentParser(description="Secure File Encryptor")
    parser.add_argument('-e', '--encrypt', action='store_true', help="Encrypt the input file")
    parser.add_argument('-d', '--decrypt', action='store_true', help="Decrypt the input file")
    parser.add_argument('-i', '--input', required=True, help="Input file path")
    parser.add_argument('-o', '--output', help="Output file path (optional)")
    parser.add_argument('--delete', action='store_true', help="Securely delete the original file after encryption")
    
    args = parser.parse_args()
    
    if not args.encrypt and not args.decrypt:
        parser.error("Must specify either -e/--encrypt or -d/--decrypt")
        
    if args.encrypt and args.decrypt:
        parser.error("Cannot specify both encrypt and decrypt")
        
    if not os.path.exists(args.input):
        parser.error(f"Input file does not exist: {args.input}")
        
    # Generate default output path if not specified
    if not args.output:
        input_path = Path(args.input)
        if args.encrypt:
            args.output = str(input_path.with_suffix(input_path.suffix + '.enc'))
        else:
            args.output = str(input_path.with_suffix(''.join(input_path.suffixes[:-1])))
            
    # Get passphrase
    import getpass
    passphrase = getpass.getpass("Enter passphrase: ")
    
    encryptor = SecureFileEncryptor()
    try:
        if args.encrypt:
            encryptor.encrypt_file(args.input, args.output, passphrase, args.delete)
            print(f"\nFile encrypted successfully: {args.output}")
        else:
            encryptor.decrypt_file(args.input, args.output, passphrase)
            print(f"\nFile decrypted successfully: {args.output}")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main() 