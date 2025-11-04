#!/usr/bin/env python3
"""
Test script for cryptographic components
"""

import sys
import os

def test_crypto_engine():
    """Test the crypto engine"""
    print("Testing Crypto Engine...")

    from crypto_engine import CryptoEngine

    # Initialize crypto with test passphrase
    crypto = CryptoEngine(data_dir=".test_secure_chat")
    success = crypto.initialize_keys("test_passphrase_123")

    if not success:
        print("❌ Failed to initialize crypto engine")
        return False

    print("✅ Crypto engine initialized")

    # Test encryption/decryption
    message = "Hello, this is a secret message!"
    recipient_key = crypto.get_public_key_hex()

    encrypted = crypto.encrypt_message(message, recipient_key)
    print(f"✅ Message encrypted: {encrypted['ciphertext'][:32]}...")

    decrypted = crypto.decrypt_message(encrypted)
    print(f"✅ Message decrypted: {decrypted}")

    if decrypted == message:
        print("✅ Encryption/Decryption successful!")
    else:
        print("❌ Encryption/Decryption failed!")
        return False

    # Test local encryption
    local_data = "This is local data"
    encrypted_local = crypto.encrypt_local_data(local_data)
    decrypted_local = crypto.decrypt_local_data(encrypted_local)

    if decrypted_local == local_data:
        print("✅ Local encryption/decryption successful!")
    else:
        print("❌ Local encryption/decryption failed!")
        return False

    return True


def test_word_encoder():
    """Test the word encoder"""
    print("\nTesting Word Encoder...")

    from word_encoder import WordEncoder

    # Test public key encoding
    test_key = "a" * 64  # Fake hex key
    words = WordEncoder.encode_public_key_to_words(test_key)
    print(f"✅ Public key encoded to {len(words)} words:")
    print(f"   {WordEncoder.format_words_for_display(words)}")

    # Test IP encoding
    test_ip = "192.168.1.100"
    ip_words = WordEncoder.encode_ip_to_words(test_ip)
    print(f"✅ IP encoded to {len(ip_words)} words:")
    print(f"   {WordEncoder.format_words_for_display(ip_words)}")

    # Test fingerprint
    fingerprint = WordEncoder.create_fingerprint(test_key, test_ip)
    print("✅ Fingerprint created:")
    print(fingerprint)

    return True


def test_obfuscation():
    """Test traffic obfuscation"""
    print("\nTesting Traffic Obfuscation...")

    from obfuscation import TrafficObfuscator, ProtocolWrapper

    # Test message wrapping
    test_message = {
        'type': 'test',
        'content': 'This is a test message',
        'timestamp': '2024-01-01T00:00:00'
    }

    wrapped = TrafficObfuscator.wrap_message(test_message)
    print(f"✅ Message wrapped: {len(wrapped)} bytes")

    unwrapped, bytes_consumed = TrafficObfuscator.unwrap_message(wrapped)
    print(f"✅ Message unwrapped: {bytes_consumed} bytes consumed")

    if unwrapped == test_message:
        print("✅ Wrap/Unwrap successful!")
    else:
        print("❌ Wrap/Unwrap failed!")
        return False

    # Test protocol wrapper
    protocol = ProtocolWrapper()
    handshake = protocol.initiate_handshake()
    print(f"✅ Handshake created: {len(handshake)} bytes")

    if protocol.process_handshake(handshake):
        print("✅ Handshake processed successfully!")
    else:
        print("❌ Handshake processing failed!")
        return False

    return True


def cleanup():
    """Clean up test files"""
    import shutil
    test_dir = ".test_secure_chat"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    print("\n🧹 Cleaned up test files")


def main():
    """Run all tests"""
    print("=" * 60)
    print("🔐 Secure P2P Chat - Component Tests")
    print("=" * 60)
    print()

    try:
        # Test crypto engine
        if not test_crypto_engine():
            print("\n❌ Crypto engine tests failed!")
            return 1

        # Test word encoder
        if not test_word_encoder():
            print("\n❌ Word encoder tests failed!")
            return 1

        # Test obfuscation
        if not test_obfuscation():
            print("\n❌ Obfuscation tests failed!")
            return 1

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)

        return 0

    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        return 1

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        cleanup()


if __name__ == "__main__":
    sys.exit(main())
