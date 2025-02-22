use aes_gcm::{Aes256Gcm, Key, Nonce};
use aes_gcm::aead::{Aead, NewAead};
use pbkdf2::pbkdf2_hmac;
use sha2::Sha256;

pub struct Encryptor {
    salt_size: usize,
    nonce_size: usize,
}

impl Encryptor {
    pub fn new() -> Self {
        Self {
            salt_size: 16,
            nonce_size: 12,
        }
    }

    pub fn encrypt(&self, data: &[u8], passphrase: &str) -> Result<Vec<u8>, String> {
        let mut salt = vec![0u8; self.salt_size];
        getrandom::getrandom(&mut salt).map_err(|e| e.to_string())?;

        let key = self.derive_key(passphrase.as_bytes(), &salt);
        let cipher = Aes256Gcm::new(&key);
        
        let mut nonce = vec![0u8; self.nonce_size];
        getrandom::getrandom(&mut nonce).map_err(|e| e.to_string())?;
        
        let encrypted = cipher
            .encrypt(Nonce::from_slice(&nonce), data)
            .map_err(|e| e.to_string())?;

        let mut result = Vec::new();
        result.extend_from_slice(&salt);
        result.extend_from_slice(&nonce);
        result.extend_from_slice(&encrypted);
        
        Ok(result)
    }

    fn derive_key(&self, passphrase: &[u8], salt: &[u8]) -> Key<Aes256Gcm> {
        let mut key = [0u8; 32];
        pbkdf2_hmac::<Sha256>(passphrase, salt, 100_000, &mut key);
        Key::<Aes256Gcm>::from_slice(&key).clone()
    }
} 