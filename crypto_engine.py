"""
Cryptographic Engine for Secure P2P Chat
Provides end-to-end encryption using NaCl (libsodium)
"""

import nacl.secret
import nacl.public
import nacl.utils
import nacl.hash
import nacl.encoding
import nacl.signing
import os
import json
from typing import Tuple, Optional
from pathlib import Path


class CryptoEngine:
    """Handles all cryptographic operations for the secure chat"""

    def __init__(self, data_dir: str = ".secure_chat"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.private_key: Optional[nacl.public.PrivateKey] = None
        self.public_key: Optional[nacl.public.PublicKey] = None
        self.signing_key: Optional[nacl.signing.SigningKey] = None
        self.verify_key: Optional[nacl.signing.VerifyKey] = None

        # Local encryption key (derived from passphrase)
        self.local_key: Optional[nacl.secret.SecretBox] = None

    def initialize_keys(self, passphrase: str) -> bool:
        """Initialize or load encryption keys"""
        # Validate passphrase
        if not passphrase:
            print("[SECURITY WARNING] Empty passphrase is highly insecure!")
            return False

        if len(passphrase) < 8:
            print(f"[SECURITY WARNING] Passphrase should be at least 8 characters (current: {len(passphrase)})")
            # Still allow but warn

        key_file = self.data_dir / "identity.enc"

        # Derive local encryption key from passphrase
        passphrase_hash = nacl.hash.blake2b(
            passphrase.encode('utf-8'),
            digest_size=32,
            encoder=nacl.encoding.RawEncoder
        )
        self.local_key = nacl.secret.SecretBox(passphrase_hash)

        if key_file.exists():
            # Load existing keys
            return self._load_keys(key_file)
        else:
            # Generate new keys
            return self._generate_keys(key_file)

    def _generate_keys(self, key_file: Path) -> bool:
        """Generate new key pairs"""
        try:
            # Generate encryption key pair (X25519)
            self.private_key = nacl.public.PrivateKey.generate()
            self.public_key = self.private_key.public_key

            # Generate signing key pair (Ed25519)
            self.signing_key = nacl.signing.SigningKey.generate()
            self.verify_key = self.signing_key.verify_key

            # Save encrypted keys
            self._save_keys(key_file)
            return True
        except Exception as e:
            print(f"Error generating keys: {e}")
            return False

    def _save_keys(self, key_file: Path):
        """Save keys encrypted with local passphrase"""
        keys_data = {
            'private_key': self.private_key.encode().hex(),
            'signing_key': bytes(self.signing_key).hex(),
        }

        plaintext = json.dumps(keys_data).encode('utf-8')
        encrypted = self.local_key.encrypt(plaintext)

        key_file.write_bytes(encrypted)

    def _load_keys(self, key_file: Path) -> bool:
        """Load keys from encrypted file"""
        try:
            encrypted = key_file.read_bytes()
            plaintext = self.local_key.decrypt(encrypted)
            keys_data = json.loads(plaintext.decode('utf-8'))

            self.private_key = nacl.public.PrivateKey(
                bytes.fromhex(keys_data['private_key'])
            )
            self.public_key = self.private_key.public_key

            self.signing_key = nacl.signing.SigningKey(
                bytes.fromhex(keys_data['signing_key'])
            )
            self.verify_key = self.signing_key.verify_key

            return True
        except Exception as e:
            print(f"Error loading keys (wrong passphrase?): {e}")
            return False

    def get_public_key_hex(self) -> str:
        """Get public key as hex string"""
        return self.public_key.encode().hex()

    def get_verify_key_hex(self) -> str:
        """Get verification key as hex string"""
        return bytes(self.verify_key).hex()

    def encrypt_message(self, message: str, recipient_public_key_hex: str) -> dict:
        """Encrypt a message for a specific recipient"""
        try:
            recipient_public_key = nacl.public.PublicKey(
                bytes.fromhex(recipient_public_key_hex)
            )

            # Create encryption box
            box = nacl.public.Box(self.private_key, recipient_public_key)

            # Encrypt message
            encrypted = box.encrypt(message.encode('utf-8'))

            # Sign the encrypted message
            signed = self.signing_key.sign(encrypted)

            return {
                'ciphertext': signed.hex(),
                'sender_public_key': self.get_public_key_hex(),
                'sender_verify_key': self.get_verify_key_hex()
            }
        except Exception as e:
            raise Exception(f"Encryption failed: {e}")

    def decrypt_message(self, encrypted_data: dict) -> str:
        """Decrypt and verify a message"""
        try:
            # Get sender's keys
            sender_public_key = nacl.public.PublicKey(
                bytes.fromhex(encrypted_data['sender_public_key'])
            )
            sender_verify_key = nacl.signing.VerifyKey(
                bytes.fromhex(encrypted_data['sender_verify_key'])
            )

            # Verify signature
            signed_message = bytes.fromhex(encrypted_data['ciphertext'])
            verified = sender_verify_key.verify(signed_message)

            # Create decryption box
            box = nacl.public.Box(self.private_key, sender_public_key)

            # Decrypt message
            plaintext = box.decrypt(verified)

            return plaintext.decode('utf-8')
        except Exception as e:
            raise Exception(f"Decryption failed: {e}")

    def encrypt_local_data(self, data: str) -> bytes:
        """Encrypt data for local storage"""
        return self.local_key.encrypt(data.encode('utf-8'))

    def decrypt_local_data(self, encrypted: bytes) -> str:
        """Decrypt locally stored data"""
        return self.local_key.decrypt(encrypted).decode('utf-8')

    def generate_session_key(self) -> bytes:
        """Generate a random session key"""
        return nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
