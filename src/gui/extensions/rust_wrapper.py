class RustEncryption:
    def __init__(self):
        try:
            import rust_encryption
            self.encryptor = rust_encryption.Encryptor()
            self.available = True
        except ImportError:
            self.available = False 