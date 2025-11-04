# 🔐 Secure P2P Chat

A highly secure, peer-to-peer encrypted chat application with traffic obfuscation and end-to-end encryption.

## 🌟 Features

### Security Features
- **End-to-End Encryption**: All messages encrypted using NaCl (libsodium) with X25519 key exchange and XSalsa20-Poly1305 authenticated encryption
- **Digital Signatures**: Messages signed using Ed25519 for authenticity verification
- **Local Encryption**: All local data (messages, keys) encrypted with passphrase-derived key using Blake2b
- **Perfect Forward Secrecy**: Each session uses ephemeral keys
- **Traffic Obfuscation**: Messages wrapped with pseudo-SSH handshake and random padding to make traffic analysis harder
- **Length Hiding**: Message lengths obscured with random padding
- **Timing Jitter**: Random delays added to hide traffic patterns

### Trust & Verification
- **Word-Based Fingerprints**: Public keys and IPs converted to memorable word sequences (PGP word list)
- **Visual Verification**: Easy-to-verify fingerprints for mutual trust establishment
- **No Central Authority**: Pure P2P architecture, no servers required

### Privacy Features
- **No Metadata Leakage**: Messages contain only encrypted content
- **Local-Only Storage**: All data stored locally with encryption
- **No Cloud Dependencies**: Completely offline-capable

### User Experience
- **Discord-Like GUI**: Modern, intuitive interface using customtkinter
- **Real-Time Messaging**: WebSocket-based instant message delivery
- **Message History**: Encrypted local message history
- **Multi-Peer Support**: Connect to multiple peers simultaneously

## 🏗️ Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                      GUI Layer                          │
│              (customtkinter interface)                  │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                     │
│        (Message handling, peer management)              │
└─────────────────────────────────────────────────────────┘
                          ↕
┌──────────────────┬──────────────────┬──────────────────┐
│   Crypto Engine  │  Local Storage   │   P2P Network    │
│  (E2E Encryption)│  (SQLite + Enc)  │   (WebSocket)    │
└──────────────────┴──────────────────┴──────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│              Traffic Obfuscation Layer                  │
│     (Pseudo-SSH handshake, padding, jitter)            │
└─────────────────────────────────────────────────────────┘
```

### Cryptographic Stack

1. **Key Generation**
   - X25519 keys for Diffie-Hellman key exchange
   - Ed25519 keys for digital signatures
   - Blake2b for passphrase hashing

2. **Message Encryption Flow**
   ```
   Plaintext → XSalsa20-Poly1305 → Sign with Ed25519 →
   Wrap with protocol → Add padding → Send via WebSocket
   ```

3. **Local Storage Encryption**
   - Passphrase → Blake2b → 256-bit key → XSalsa20-Poly1305

### Traffic Obfuscation

1. **Connection Phase**
   - Fake SSH banner: `SSH-2.0-OpenSSH_8.9`
   - Random key exchange data
   - Makes initial connection look like SSH

2. **Message Phase**
   - Protocol wrapper with length fields
   - Random padding (16-256 bytes)
   - Timing jitter (10-100ms)
   - Optional length obfuscation to fixed size

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download this repository**
   ```bash
   cd secure-p2p-chat
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python gui.py
   ```

## 🚀 Usage

### First Launch

1. **Create Identity**
   - Enter a strong passphrase (minimum 8 characters)
   - This passphrase encrypts your identity and local data
   - **IMPORTANT**: Store this passphrase securely - it cannot be recovered

2. **View Your Information**
   - Click "ℹ️ My Info" to see your address and fingerprint
   - Share your address (IP:PORT) with peers you want to connect with

### Connecting to Peers

1. **Exchange Information**
   - Share your address with a trusted peer
   - Obtain their address

2. **Connect**
   - Click "+ Connect to Peer"
   - Enter peer address in format: `IP:PORT` (e.g., `192.168.1.100:8765`)
   - Wait for connection to establish

3. **Verify Fingerprint**
   - Both users should verify each other's fingerprints
   - Fingerprints are shown as memorable word sequences
   - Verify these words match what your peer sees

### Sending Messages

1. Select a peer from the conversation list
2. Type your message in the input box
3. Press Enter or click Send
4. Messages are automatically encrypted before sending

## 🔒 Security Considerations

### Strong Security Practices

✅ **DO**:
- Use a strong, unique passphrase
- Verify fingerprints with peers through a secondary channel (phone call, in person)
- Keep your passphrase secure and private
- Run the application on a trusted device
- Use secure networks when possible

❌ **DON'T**:
- Share your passphrase with anyone
- Use weak or common passphrases
- Connect to untrusted peers without verification
- Use on compromised devices
- Assume the network is secure

### Threat Model

**Protected Against**:
- Network eavesdropping (passive monitoring)
- Message tampering
- Identity spoofing (with fingerprint verification)
- Traffic pattern analysis (partial)
- Local storage compromise (with strong passphrase)

**Not Protected Against**:
- Compromised endpoints (keyloggers, malware)
- Physical access to unlocked device
- Weak passphrase attacks
- Advanced persistent threats with endpoint access
- Quantum computers (in the future - would need post-quantum crypto)

### Known Limitations

1. **No Perfect Deniability**: Messages are digitally signed
2. **IP Exposure**: Peer IP addresses are visible to connected peers
3. **No Built-in Anonymity**: Not a Tor/I2P replacement
4. **Limited Traffic Analysis Resistance**: Obfuscation helps but is not foolproof
5. **No Multi-Device Sync**: Each device has separate identity

## 🛠️ Technical Details

### Cryptographic Primitives

| Component | Algorithm | Key Size |
|-----------|-----------|----------|
| Key Exchange | X25519 (ECDH) | 256 bits |
| Encryption | XSalsa20 | 256 bits |
| Authentication | Poly1305 | 128 bits |
| Signatures | Ed25519 | 256 bits |
| Hashing | Blake2b | 256 bits |

### Network Protocol

```
Handshake Phase:
1. TCP Connection established
2. WebSocket upgrade
3. Fake SSH banner exchange
4. Identity exchange (public keys)

Message Phase:
┌──────────────────────────────────────────┐
│ Total Length (4 bytes)                   │
├──────────────────────────────────────────┤
│ Payload Length (4 bytes)                 │
├──────────────────────────────────────────┤
│ Encrypted + Signed Message (variable)    │
├──────────────────────────────────────────┤
│ Random Padding (16-256 bytes)            │
└──────────────────────────────────────────┘
```

### File Structure

```
.
├── crypto_engine.py      # Cryptographic operations
├── p2p_network.py        # P2P networking layer
├── obfuscation.py        # Traffic obfuscation
├── word_encoder.py       # Fingerprint word encoding
├── local_storage.py      # Encrypted local storage
├── gui.py                # GUI application
├── requirements.txt      # Dependencies
└── README.md            # This file

Data Directory (~/.secure_chat/):
├── identity.enc          # Encrypted identity keys
└── messages.db          # Encrypted message database
```

## 🔧 Configuration

### Default Settings

- **Port**: 8765 (configurable in code)
- **Max Message Size**: 10 MB
- **Padding Range**: 16-256 bytes
- **Timing Jitter**: 10-100 ms
- **Data Directory**: `.secure_chat` in home directory

### Customization

Edit the respective files:
- `p2p_network.py`: Network settings (port, timeouts)
- `obfuscation.py`: Obfuscation parameters (padding, jitter)
- `gui.py`: GUI appearance and behavior

## 🐛 Troubleshooting

### Connection Issues

**Problem**: Cannot connect to peer
- Check firewall settings (allow port 8765)
- Verify peer is running and accessible
- Ensure correct IP address format (IP:PORT)
- Try connecting from both sides

**Problem**: Connection drops frequently
- Check network stability
- Verify no aggressive firewall rules
- Increase timeout values if needed

### Encryption Issues

**Problem**: "Wrong passphrase" error
- Ensure correct passphrase (case-sensitive)
- If truly forgotten, delete `.secure_chat` directory (loses all data)

**Problem**: "Decryption failed"
- Peer may have different identity
- Message may be corrupted
- Check network integrity

## 📚 Dependencies

- **PyNaCl** (1.5.0): Python bindings for libsodium (cryptography)
- **websockets** (12.0): WebSocket implementation
- **customtkinter** (5.2.1): Modern GUI framework

## 🤝 Contributing

This is a security-focused project. If you find vulnerabilities:
1. **Do not** open public issues for security vulnerabilities
2. Contact the maintainers privately
3. Allow time for fixes before disclosure

## ⚖️ License

This project is for educational and research purposes. Use responsibly and in accordance with local laws.

## 🔮 Future Enhancements

Potential improvements:
- [ ] Post-quantum cryptography support
- [ ] Group chat functionality
- [ ] File transfer capability
- [ ] Audio/video calling
- [ ] Better traffic analysis resistance (constant-rate traffic)
- [ ] Tor integration for anonymity
- [ ] Mobile app versions
- [ ] Perfect forward secrecy with ratcheting (Double Ratchet)
- [ ] Deniable authentication
- [ ] Multi-device support

## ⚠️ Disclaimer

This software is provided "as is" without warranty. The authors are not responsible for any damages or misuse. This is an educational project - for critical communications, use professionally audited solutions like Signal.

## 📞 Support

For issues, questions, or discussions, please open an issue on the repository.

---

**Remember**: The security of this system depends on:
1. Strong passphrases
2. Secure endpoints
3. Proper fingerprint verification
4. Trusted peers
5. Good operational security practices

Stay safe and chat securely! 🔐
