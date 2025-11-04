# Quick Start Guide

## Installation (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Test Installation
```bash
python3 test_crypto.py
```

If tests pass, you're ready to go! ✅

### Step 3: Launch Application
```bash
python3 gui.py
# or
./start.sh
```

## First Time Setup

### 1. Create Your Identity
- Enter a strong passphrase (minimum 8 characters)
- Remember it - you'll need it every time!
- Your keys are generated automatically

### 2. Get Your Address
- Click "ℹ️ My Info" button
- Your address will be shown as `IP:PORT`
- Share this with trusted peers

### 3. Connect to a Friend

**Both users should:**
1. Start the application
2. Share addresses with each other

**Then either user can:**
1. Click "+ Connect to Peer"
2. Enter friend's address (e.g., `192.168.1.50:8765`)
3. Wait for connection

### 4. Verify Security
- Both users should verify fingerprints
- Fingerprints shown as memorable words
- Verify through secondary channel (phone call, in person)
- If words match → ✅ Secure connection!

### 5. Start Chatting
- Select conversation from list
- Type message and press Enter
- All messages encrypted automatically!

## Example Scenario

**Alice (192.168.1.100):**
1. Runs `python3 gui.py`
2. Enters passphrase
3. Sees her address: `192.168.1.100:8765`
4. Tells Bob her address via phone

**Bob (192.168.1.200):**
1. Runs `python3 gui.py`
2. Enters passphrase
3. Clicks "+ Connect to Peer"
4. Enters: `192.168.1.100:8765`
5. Sees Alice appear in peer list

**Both verify fingerprints and start chatting!**

## Firewall Configuration

If connections fail, open the port:

**Linux:**
```bash
sudo ufw allow 8765/tcp
```

**macOS:**
```bash
# System Preferences → Security & Privacy → Firewall → Allow
```

**Windows:**
```bash
netsh advfirewall firewall add rule name="P2PChat" dir=in action=allow protocol=TCP localport=8765
```

## Troubleshooting

### "Cannot connect to peer"
- Check firewall (port 8765)
- Verify IP address is correct
- Ensure both users are running the app
- Try connecting from both sides

### "Wrong passphrase"
- Passphrase is case-sensitive
- If forgotten, delete `.secure_chat` folder (loses all data!)

### "Module not found"
- Run: `pip install -r requirements.txt`

## Security Checklist

Before chatting:
- ✅ Used strong passphrase
- ✅ Verified peer's fingerprint
- ✅ Running on trusted device
- ✅ Understand who can see what

What's encrypted:
- ✅ Message content
- ✅ Local storage
- ✅ Your private keys

What's NOT hidden:
- ❌ IP addresses (peers see your IP)
- ❌ Connection timing
- ❌ That you're communicating

## Network Scenarios

### Same Local Network (easiest)
- Use local IP (192.168.x.x)
- No router config needed
- Works immediately

### Different Networks (requires setup)
- Need port forwarding on router
- Forward port 8765 to your computer
- Use public IP address
- Security: only connect to trusted peers!

### VPN/Tunnel (most secure)
- Use VPN IP addresses
- Works like local network
- Adds extra security layer

## Tips

1. **Keep it simple**: Start with local network testing
2. **Verify always**: Always check fingerprints
3. **Strong passphrases**: Use 12+ characters, mix of types
4. **Regular backups**: Your passphrase can't be recovered!
5. **Trust carefully**: Only connect to people you trust

## Next Steps

After basic usage:
- Read README.md for security details
- Understand the threat model
- Learn about traffic obfuscation
- Explore the code to understand how it works

## Getting Help

- Check README.md for detailed information
- Run tests: `python3 test_crypto.py`
- Check GitHub issues

---

**Remember**: Security requires both good tools AND good practices! 🔐
