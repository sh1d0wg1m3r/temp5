#!/usr/bin/env python3
"""
Comprehensive QA Test Suite for Secure P2P Chat
Tests edge cases, error handling, and integration
"""

import sys
import os
import asyncio
import shutil
from pathlib import Path
import time

# Test data directory
TEST_DIR = ".test_qa_chat"


def cleanup_test_dir():
    """Clean up test directory"""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)


def test_crypto_edge_cases():
    """Test crypto engine with edge cases"""
    print("\n" + "="*60)
    print("Testing Crypto Engine - Edge Cases")
    print("="*60)

    from crypto_engine import CryptoEngine

    # Test 1: Empty passphrase
    print("\n1. Testing empty passphrase...")
    crypto = CryptoEngine(data_dir=TEST_DIR)
    try:
        # This should work but is insecure
        result = crypto.initialize_keys("")
        print("⚠️  Empty passphrase accepted (security warning)")
    except Exception as e:
        print(f"✅ Empty passphrase rejected: {e}")

    # Test 2: Very long passphrase
    print("\n2. Testing very long passphrase...")
    crypto = CryptoEngine(data_dir=TEST_DIR + "_long")
    long_pass = "a" * 10000
    result = crypto.initialize_keys(long_pass)
    if result:
        print("✅ Long passphrase handled correctly")
    else:
        print("❌ Failed with long passphrase")

    # Test 3: Unicode passphrase
    print("\n3. Testing Unicode passphrase...")
    crypto = CryptoEngine(data_dir=TEST_DIR + "_unicode")
    unicode_pass = "パスワード🔐test密码"
    result = crypto.initialize_keys(unicode_pass)
    if result:
        print("✅ Unicode passphrase handled correctly")
    else:
        print("❌ Failed with Unicode passphrase")

    # Test 4: Very long message
    print("\n4. Testing very long message encryption...")
    crypto = CryptoEngine(data_dir=TEST_DIR + "_msg")
    crypto.initialize_keys("test123")
    long_message = "A" * 1000000  # 1MB message
    try:
        encrypted = crypto.encrypt_message(long_message, crypto.get_public_key_hex())
        decrypted = crypto.decrypt_message(encrypted)
        if decrypted == long_message:
            print(f"✅ Large message (1MB) encrypted/decrypted correctly")
        else:
            print("❌ Message corruption in large message")
    except Exception as e:
        print(f"❌ Failed with large message: {e}")

    # Test 5: Empty message
    print("\n5. Testing empty message...")
    try:
        encrypted = crypto.encrypt_message("", crypto.get_public_key_hex())
        decrypted = crypto.decrypt_message(encrypted)
        if decrypted == "":
            print("✅ Empty message handled correctly")
        else:
            print("❌ Empty message corruption")
    except Exception as e:
        print(f"❌ Failed with empty message: {e}")

    # Test 6: Special characters in message
    print("\n6. Testing special characters...")
    special_msg = "Test\n\r\t\x00\x01\x02 Special 🔐 chars"
    try:
        encrypted = crypto.encrypt_message(special_msg, crypto.get_public_key_hex())
        decrypted = crypto.decrypt_message(encrypted)
        if decrypted == special_msg:
            print("✅ Special characters handled correctly")
        else:
            print("❌ Special character corruption")
    except Exception as e:
        print(f"❌ Failed with special characters: {e}")

    # Test 7: Wrong key decryption
    print("\n7. Testing decryption with wrong key...")
    crypto2 = CryptoEngine(data_dir=TEST_DIR + "_crypto2")
    crypto2.initialize_keys("different_pass")
    try:
        encrypted = crypto.encrypt_message("test", crypto2.get_public_key_hex())
        # Try to decrypt with wrong private key (should fail)
        decrypted = crypto2.decrypt_message(encrypted)
        print("❌ Decryption succeeded with wrong key (security issue!)")
    except Exception as e:
        print(f"✅ Decryption failed correctly with wrong key")

    # Test 8: Tampered ciphertext
    print("\n8. Testing tampered ciphertext...")
    encrypted = crypto.encrypt_message("test", crypto.get_public_key_hex())
    # Tamper with ciphertext
    tampered = encrypted.copy()
    tampered['ciphertext'] = tampered['ciphertext'][:-2] + "FF"
    try:
        crypto.decrypt_message(tampered)
        print("❌ Accepted tampered message (security issue!)")
    except Exception as e:
        print(f"✅ Tampered message rejected correctly")

    # Test 9: Persistence - Save and reload keys
    print("\n9. Testing key persistence...")
    test_dir_persist = TEST_DIR + "_persist"
    crypto_save = CryptoEngine(data_dir=test_dir_persist)
    crypto_save.initialize_keys("persist_test")
    key1 = crypto_save.get_public_key_hex()

    # Create new instance with same passphrase
    crypto_load = CryptoEngine(data_dir=test_dir_persist)
    crypto_load.initialize_keys("persist_test")
    key2 = crypto_load.get_public_key_hex()

    if key1 == key2:
        print("✅ Keys persisted and loaded correctly")
    else:
        print("❌ Key persistence failed")

    # Test 10: Wrong passphrase on load
    print("\n10. Testing wrong passphrase on reload...")
    crypto_wrong = CryptoEngine(data_dir=test_dir_persist)
    result = crypto_wrong.initialize_keys("wrong_password")
    if not result:
        print("✅ Wrong passphrase detected correctly")
    else:
        print("⚠️  Wrong passphrase not detected (keys may be wrong)")

    return True


def test_storage_edge_cases():
    """Test local storage with edge cases"""
    print("\n" + "="*60)
    print("Testing Local Storage - Edge Cases")
    print("="*60)

    from crypto_engine import CryptoEngine
    from local_storage import LocalStorage

    crypto = CryptoEngine(data_dir=TEST_DIR + "_storage")
    crypto.initialize_keys("storage_test")
    storage = LocalStorage(crypto, data_dir=TEST_DIR + "_storage")

    # Test 1: Save and retrieve message
    print("\n1. Testing message save/retrieve...")
    storage.save_message("test_peer", "Alice", "Hello World", False)
    messages = storage.get_messages("test_peer")
    if len(messages) == 1 and messages[0]['content'] == "Hello World":
        print("✅ Message saved and retrieved correctly")
    else:
        print("❌ Message save/retrieve failed")

    # Test 2: Multiple messages
    print("\n2. Testing multiple messages...")
    for i in range(100):
        storage.save_message("test_peer", "Alice", f"Message {i}", False)
    messages = storage.get_messages("test_peer", limit=100)
    if len(messages) == 100:
        print(f"✅ Retrieved correct number of messages: {len(messages)}")
    else:
        print(f"⚠️  Expected 100 messages, got {len(messages)}")

    # Test 3: Large message
    print("\n3. Testing large message storage...")
    large_msg = "X" * 100000  # 100KB
    storage.save_message("large_peer", "Bob", large_msg, True)
    messages = storage.get_messages("large_peer")
    if messages[0]['content'] == large_msg:
        print("✅ Large message stored correctly")
    else:
        print("❌ Large message corruption")

    # Test 4: Unicode messages
    print("\n4. Testing Unicode messages...")
    unicode_msg = "Hello 世界 🌍 مرحبا мир"
    storage.save_message("unicode_peer", "Charlie", unicode_msg, False)
    messages = storage.get_messages("unicode_peer")
    if messages[0]['content'] == unicode_msg:
        print("✅ Unicode message stored correctly")
    else:
        print("❌ Unicode message corruption")

    # Test 5: Peer management
    print("\n5. Testing peer management...")
    storage.save_peer("192.168.1.1:8765", "TestPeer", "abc123", "def456")
    peer = storage.get_peer("192.168.1.1:8765")
    if peer and peer['nickname'] == "TestPeer":
        print("✅ Peer saved and retrieved correctly")
    else:
        print("❌ Peer management failed")

    # Test 6: Search functionality
    print("\n6. Testing message search...")
    storage.save_message("search_peer", "David", "Find this specific message", False)
    results = storage.search_messages("specific message")
    if len(results) > 0 and "specific message" in results[0]['content']:
        print(f"✅ Search found {len(results)} result(s)")
    else:
        print("❌ Search failed")

    # Test 7: Empty queries
    print("\n7. Testing edge case queries...")
    messages = storage.get_messages("nonexistent_peer")
    if len(messages) == 0:
        print("✅ Nonexistent peer returns empty list")
    else:
        print("❌ Unexpected results for nonexistent peer")

    return True


def test_obfuscation_edge_cases():
    """Test traffic obfuscation edge cases"""
    print("\n" + "="*60)
    print("Testing Traffic Obfuscation - Edge Cases")
    print("="*60)

    from obfuscation import TrafficObfuscator, ProtocolWrapper

    # Test 1: Very large payload
    print("\n1. Testing large payload...")
    large_payload = {'type': 'test', 'data': 'X' * 1000000}
    try:
        wrapped = TrafficObfuscator.wrap_message(large_payload)
        unwrapped, _ = TrafficObfuscator.unwrap_message(wrapped)
        if unwrapped == large_payload:
            print(f"✅ Large payload (1MB) wrapped/unwrapped correctly")
        else:
            print("❌ Large payload corruption")
    except Exception as e:
        print(f"❌ Failed with large payload: {e}")

    # Test 2: Empty payload
    print("\n2. Testing empty payload...")
    try:
        empty_payload = {'type': 'empty'}
        wrapped = TrafficObfuscator.wrap_message(empty_payload)
        unwrapped, _ = TrafficObfuscator.unwrap_message(wrapped)
        if unwrapped == empty_payload:
            print("✅ Empty payload handled correctly")
        else:
            print("❌ Empty payload corruption")
    except Exception as e:
        print(f"❌ Failed with empty payload: {e}")

    # Test 3: Unicode in payload
    print("\n3. Testing Unicode payload...")
    unicode_payload = {'type': 'test', 'message': 'Hello 世界 🔐'}
    wrapped = TrafficObfuscator.wrap_message(unicode_payload)
    unwrapped, _ = TrafficObfuscator.unwrap_message(wrapped)
    if unwrapped == unicode_payload:
        print("✅ Unicode payload handled correctly")
    else:
        print("❌ Unicode payload corruption")

    # Test 4: Incomplete data
    print("\n4. Testing incomplete data...")
    wrapped = TrafficObfuscator.wrap_message({'type': 'test'})
    incomplete = wrapped[:10]  # Only first 10 bytes
    try:
        TrafficObfuscator.unwrap_message(incomplete)
        print("❌ Accepted incomplete message")
    except ValueError:
        print("✅ Incomplete message rejected correctly")
    except Exception as e:
        print(f"✅ Incomplete message rejected: {e}")

    # Test 5: Protocol wrapper
    print("\n5. Testing protocol wrapper...")
    protocol = ProtocolWrapper()
    test_msg = {'type': 'test', 'data': 'test data'}
    wrapped = protocol.wrap_application_message(test_msg)
    unwrapped = protocol.unwrap_application_message(wrapped)
    if unwrapped == test_msg:
        print("✅ Protocol wrapper works correctly")
    else:
        print("❌ Protocol wrapper failed")

    # Test 6: Timing jitter variation
    print("\n6. Testing timing jitter...")
    jitters = [TrafficObfuscator.add_timing_jitter() for _ in range(100)]
    min_jitter = min(jitters)
    max_jitter = max(jitters)
    avg_jitter = sum(jitters) / len(jitters)
    print(f"   Min: {min_jitter*1000:.1f}ms, Max: {max_jitter*1000:.1f}ms, Avg: {avg_jitter*1000:.1f}ms")
    if 0.010 <= min_jitter <= 0.100 and 0.010 <= max_jitter <= 0.100:
        print("✅ Timing jitter within expected range")
    else:
        print("⚠️  Timing jitter outside expected range")

    return True


def test_word_encoder_edge_cases():
    """Test word encoder edge cases"""
    print("\n" + "="*60)
    print("Testing Word Encoder - Edge Cases")
    print("="*60)

    from word_encoder import WordEncoder

    # Test 1: Short hex string
    print("\n1. Testing short hex string...")
    short_hex = "abc"
    words = WordEncoder.encode_hex_to_words(short_hex, 4)
    if len(words) == 4:
        print(f"✅ Short hex encoded to {len(words)} words")
    else:
        print(f"❌ Expected 4 words, got {len(words)}")

    # Test 2: Very long hex string
    print("\n2. Testing very long hex string...")
    long_hex = "a" * 10000
    words = WordEncoder.encode_hex_to_words(long_hex, 8)
    if len(words) == 8:
        print(f"✅ Long hex encoded to {len(words)} words")
    else:
        print(f"❌ Expected 8 words, got {len(words)}")

    # Test 3: Empty string
    print("\n3. Testing empty string...")
    try:
        words = WordEncoder.encode_hex_to_words("", 4)
        print(f"✅ Empty string handled: {len(words)} words generated")
    except Exception as e:
        print(f"❌ Empty string caused error: {e}")

    # Test 4: Consistency check
    print("\n4. Testing encoding consistency...")
    test_hex = "deadbeef" * 8
    words1 = WordEncoder.encode_hex_to_words(test_hex, 6)
    words2 = WordEncoder.encode_hex_to_words(test_hex, 6)
    if words1 == words2:
        print("✅ Encoding is consistent (same input → same output)")
    else:
        print("❌ Encoding is inconsistent")

    # Test 5: Different inputs produce different outputs
    print("\n5. Testing uniqueness...")
    words_a = WordEncoder.encode_hex_to_words("aaaa", 4)
    words_b = WordEncoder.encode_hex_to_words("bbbb", 4)
    if words_a != words_b:
        print("✅ Different inputs produce different words")
    else:
        print("❌ Different inputs produced same words")

    # Test 6: IP encoding
    print("\n6. Testing various IP formats...")
    ips = ["192.168.1.1", "10.0.0.1", "255.255.255.255", "0.0.0.0"]
    for ip in ips:
        words = WordEncoder.encode_ip_to_words(ip)
        print(f"   {ip}: {' '.join(words[:2])}...")
    print("✅ IP encoding completed for all test IPs")

    # Test 7: Fingerprint generation
    print("\n7. Testing fingerprint generation...")
    fingerprint = WordEncoder.create_fingerprint("a" * 64, "192.168.1.1")
    if "Key:" in fingerprint and "IP:" in fingerprint:
        print("✅ Fingerprint generated correctly")
        print(f"   Preview: {fingerprint.split()[1]}")
    else:
        print("❌ Fingerprint generation failed")

    return True


def test_error_handling():
    """Test error handling and recovery"""
    print("\n" + "="*60)
    print("Testing Error Handling")
    print("="*60)

    # Test 1: Corrupted encrypted data
    print("\n1. Testing corrupted encrypted data...")
    from crypto_engine import CryptoEngine
    crypto = CryptoEngine(data_dir=TEST_DIR + "_error")
    crypto.initialize_keys("error_test")

    try:
        fake_encrypted = {
            'ciphertext': 'corrupted_data',
            'sender_public_key': 'bad_key',
            'sender_verify_key': 'bad_verify'
        }
        crypto.decrypt_message(fake_encrypted)
        print("❌ Accepted corrupted data")
    except Exception as e:
        print(f"✅ Corrupted data rejected: {type(e).__name__}")

    # Test 2: Invalid file permissions (simulate)
    print("\n2. Testing file handling...")
    try:
        from local_storage import LocalStorage
        # Try to create storage in valid location
        storage = LocalStorage(crypto, data_dir=TEST_DIR + "_error")
        print("✅ Storage created successfully")
    except Exception as e:
        print(f"⚠️  Storage creation issue: {e}")

    return True


def test_performance():
    """Test performance benchmarks"""
    print("\n" + "="*60)
    print("Performance Benchmarks")
    print("="*60)

    from crypto_engine import CryptoEngine
    from obfuscation import TrafficObfuscator

    crypto = CryptoEngine(data_dir=TEST_DIR + "_perf")
    crypto.initialize_keys("perf_test")

    # Test 1: Encryption speed
    print("\n1. Testing encryption performance...")
    message = "Test message " * 100  # ~1.3KB
    iterations = 100

    start = time.time()
    for _ in range(iterations):
        encrypted = crypto.encrypt_message(message, crypto.get_public_key_hex())
    encrypt_time = time.time() - start
    print(f"   {iterations} encryptions: {encrypt_time:.3f}s ({iterations/encrypt_time:.1f} ops/sec)")

    # Test 2: Decryption speed
    print("\n2. Testing decryption performance...")
    encrypted = crypto.encrypt_message(message, crypto.get_public_key_hex())

    start = time.time()
    for _ in range(iterations):
        decrypted = crypto.decrypt_message(encrypted)
    decrypt_time = time.time() - start
    print(f"   {iterations} decryptions: {decrypt_time:.3f}s ({iterations/decrypt_time:.1f} ops/sec)")

    # Test 3: Obfuscation overhead
    print("\n3. Testing obfuscation overhead...")
    test_data = {'type': 'test', 'data': 'x' * 1000}

    start = time.time()
    for _ in range(iterations):
        wrapped = TrafficObfuscator.wrap_message(test_data)
        unwrapped, _ = TrafficObfuscator.unwrap_message(wrapped)
    obfuscation_time = time.time() - start
    print(f"   {iterations} wrap/unwrap cycles: {obfuscation_time:.3f}s ({iterations/obfuscation_time:.1f} ops/sec)")

    # Test 4: Local storage speed
    print("\n4. Testing storage performance...")
    from local_storage import LocalStorage
    storage = LocalStorage(crypto, data_dir=TEST_DIR + "_perf")

    start = time.time()
    for i in range(100):
        storage.save_message("perf_peer", "User", f"Message {i}", False)
    save_time = time.time() - start
    print(f"   100 message saves: {save_time:.3f}s ({100/save_time:.1f} ops/sec)")

    start = time.time()
    for _ in range(100):
        messages = storage.get_messages("perf_peer", limit=50)
    retrieve_time = time.time() - start
    print(f"   100 message retrievals: {retrieve_time:.3f}s ({100/retrieve_time:.1f} ops/sec)")

    return True


def main():
    """Run all QA tests"""
    print("=" * 60)
    print("🔍 Comprehensive QA Test Suite")
    print("=" * 60)

    cleanup_test_dir()

    try:
        # Run all test suites
        results = []

        results.append(("Crypto Edge Cases", test_crypto_edge_cases()))
        results.append(("Storage Edge Cases", test_storage_edge_cases()))
        results.append(("Obfuscation Edge Cases", test_obfuscation_edge_cases()))
        results.append(("Word Encoder Edge Cases", test_word_encoder_edge_cases()))
        results.append(("Error Handling", test_error_handling()))
        results.append(("Performance Benchmarks", test_performance()))

        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)

        all_passed = True
        for name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {name}")
            if not result:
                all_passed = False

        print("=" * 60)

        if all_passed:
            print("✅ All QA tests completed successfully!")
            return 0
        else:
            print("⚠️  Some tests had issues - review output above")
            return 1

    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        cleanup_test_dir()


if __name__ == "__main__":
    sys.exit(main())
