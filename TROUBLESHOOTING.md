# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### Problem: Dependencies won't install
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solution:**
```bash
# Update pip first
python3 -m pip install --upgrade pip

# Install dependencies one by one to see which fails
pip install PyNaCl
pip install websockets
pip install customtkinter

# If on Linux and PyNaCl fails, install system dependencies
sudo apt-get install python3-dev libffi-dev libsodium-dev
```

#### Problem: Permission denied when installing
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13]
```

**Solution:**
```bash
# Use --user flag
pip install --user -r requirements.txt

# Or use a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Connection Issues

#### Problem: Cannot connect to peer
**Symptoms:**
- "Connection refused" error
- "Connection timeout" error
- Nothing happens when clicking connect

**Solutions:**

1. **Check firewall**
   ```bash
   # Linux (ufw)
   sudo ufw allow 8765/tcp
   sudo ufw status

   # Linux (iptables)
   sudo iptables -A INPUT -p tcp --dport 8765 -j ACCEPT

   # Check if port is listening
   netstat -tuln | grep 8765
   ```

2. **Verify correct address**
   - Format must be `IP:PORT` (e.g., `192.168.1.100:8765`)
   - IP must be reachable from your network
   - Try pinging first: `ping 192.168.1.100`

3. **Check if peer is running**
   - Other user must have the application running
   - Their firewall must allow incoming connections
   - Try connecting from both sides

4. **Network troubleshooting**
   ```bash
   # Test if port is accessible
   telnet 192.168.1.100 8765
   # or
   nc -zv 192.168.1.100 8765
   ```

#### Problem: Connected but messages not received
**Solutions:**
1. Check fingerprints match (security feature)
2. Look for rate limit messages in console
3. Restart both applications
4. Check network stability

#### Problem: Frequent disconnections
**Solutions:**
1. Check network stability
2. Verify no aggressive firewall rules
3. Check for system sleep/hibernate settings
4. Reduce message sending rate

### Encryption/Key Issues

#### Problem: "Wrong passphrase" error on startup
**Solutions:**
1. Ensure passphrase is exactly correct (case-sensitive)
2. Check for extra spaces
3. If truly forgotten, delete `.secure_chat` directory:
   ```bash
   rm -rf ~/.secure_chat
   # WARNING: This deletes all messages and keys!
   ```

#### Problem: "Decryption failed" for received messages
**Possible Causes:**
- Peer has changed their identity
- Message corrupted in transit
- Attacker trying to send fake messages (good!)

**Solutions:**
1. Ask peer to verify their fingerprint
2. Ask peer to restart their application
3. Disconnect and reconnect
4. If persistent, both users restart with fresh connections

#### Problem: Empty passphrase warning
**Solution:**
Use a strong passphrase (8+ characters). Security tips:
- Use mix of uppercase, lowercase, numbers
- Add special characters
- Use 12+ characters for better security
- Don't reuse passwords from other services

### GUI Issues

#### Problem: Window won't open / GUI crashes
**Solutions:**

1. **Check if customtkinter is properly installed**
   ```python
   python3 -c "import customtkinter; print('OK')"
   ```

2. **Check display available (Linux)**
   ```bash
   echo $DISPLAY
   # Should show something like :0
   ```

3. **Run without GUI (future CLI mode)**
   ```bash
   # For now, GUI is required
   # Future versions may include CLI mode
   ```

4. **Check system resources**
   - Ensure enough RAM available
   - Close other applications
   - Check CPU usage

#### Problem: GUI is slow or freezing
**Solutions:**
1. Reduce message history size
2. Delete old conversations
3. Clean up message database:
   ```bash
   # Backup first!
   cp ~/.secure_chat/messages.db ~/.secure_chat/messages.db.backup
   # Consider starting fresh if very slow
   ```

### Performance Issues

#### Problem: High CPU usage
**Possible Causes:**
- Many active connections
- Large message history being decrypted
- Frequent reconnection attempts

**Solutions:**
1. Disconnect from inactive peers
2. Restart application periodically
3. Limit concurrent connections
4. Clear message history for old conversations

#### Problem: High memory usage
**Solutions:**
1. Restart application
2. Clear message history
3. Reduce number of active connections
4. Close and reopen after long sessions

#### Problem: Messages slow to send/receive
**Solutions:**
1. Check network speed
2. Verify not rate limited (100 messages/60 seconds)
3. Reduce message size
4. Check system load

### Security Warnings and Errors

#### Warning: "Passphrase should be at least 8 characters"
**Impact:** Low security
**Solution:** Use longer passphrase (12+ recommended)

#### Warning: "Rate limit exceeded"
**Impact:** Messages being dropped to prevent DoS
**Solution:** Slow down message sending rate (<100 per minute)

#### Error: "Tampered message rejected"
**Impact:** Good! Security working correctly
**What it means:**
- Someone tried to modify encrypted message
- Message corrupted in transit
- Potential attacker (rare)

**Action:**
- This is normal security behavior
- If frequent, check network quality
- Consider if someone is interfering

#### Error: "Invalid signature"
**Impact:** Message authentication failed
**Possible Causes:**
- Corrupted message
- Wrong sender identity
- Attacker impersonation attempt

**Action:**
- Verify peer's fingerprint
- Ask peer to verify their identity
- Reconnect if persistent

### Database Issues

#### Problem: Database locked error
**Solution:**
```bash
# Make sure no other instances running
ps aux | grep gui.py

# If database corrupted
cd ~/.secure_chat
sqlite3 messages.db "PRAGMA integrity_check;"

# If failed, backup and recreate
mv messages.db messages.db.broken
# Restart application to create new database
```

#### Problem: Cannot save messages
**Solutions:**
1. Check disk space: `df -h`
2. Check permissions: `ls -la ~/.secure_chat/`
3. Verify directory writeable
4. Check if disk is full

### Debugging

#### Enable Debug Logging

1. **Check log files**
   ```bash
   # Logs are in the .secure_chat directory
   cat ~/.secure_chat/chat_*.log

   # Watch logs in real-time
   tail -f ~/.secure_chat/chat_$(date +%Y%m%d).log
   ```

2. **Run tests to verify components**
   ```bash
   # Basic component tests
   python3 test_crypto.py

   # Comprehensive QA tests
   python3 qa_tests.py
   ```

3. **Check for errors in console**
   ```bash
   # Run and watch for errors
   python3 gui.py
   ```

#### Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| `[P2P] Connection closed` | Peer disconnected | Normal, will reconnect if they come back |
| `[P2P] Rate limit exceeded` | Too many messages | Slow down sending |
| `[CRYPTO] Decryption failed` | Can't decrypt message | Check fingerprints match |
| `[Storage] Error saving message` | Database issue | Check disk space and permissions |
| `Connection refused` | Can't reach peer | Check firewall and address |

### Network-Specific Issues

#### Same LAN Connection
**Setup:**
1. Both on same WiFi/Ethernet
2. Use local IP (192.168.x.x or 10.x.x.x)
3. No router configuration needed

**Troubleshooting:**
```bash
# Find your local IP
ip addr show  # Linux
ipconfig      # Windows

# Test connectivity
ping <peer_ip>
```

#### Internet Connection (Different Networks)
**Setup Required:**
1. Port forwarding on router (port 8765 → your computer)
2. Use public IP address
3. Dynamic DNS if IP changes (optional)

**Troubleshooting:**
1. Find your public IP: `curl ifconfig.me`
2. Configure router port forwarding
3. Test port is open: `nc -zv <public_ip> 8765`
4. Consider security implications

#### VPN Connection
**Setup:**
1. Both users on same VPN
2. Use VPN IP addresses
3. Usually works like LAN

**Troubleshooting:**
- Ensure VPN allows peer-to-peer
- Check VPN firewall rules
- Some VPNs block P2P traffic

### Getting More Help

#### Before Asking for Help

Collect this information:
1. Operating system and version
2. Python version: `python3 --version`
3. Error messages (full text)
4. Steps to reproduce
5. What you've already tried
6. Contents of log file

#### Where to Get Help

1. Check this troubleshooting guide
2. Review README.md for documentation
3. Run test suite to identify component issues
4. Check GitHub issues for similar problems
5. Create new GitHub issue with collected info

#### Providing Debug Information

```bash
# System information
python3 --version
pip list | grep -E "(PyNaCl|websockets|customtkinter)"
uname -a  # Linux/Mac
cat /etc/os-release  # Linux

# Network information
ip addr show
netstat -tuln | grep 8765

# Test results
python3 test_crypto.py > test_results.txt 2>&1
python3 qa_tests.py > qa_results.txt 2>&1

# Recent logs
tail -100 ~/.secure_chat/chat_*.log > recent_logs.txt
```

### Known Limitations

1. **No automatic reconnection** - Manually reconnect if connection drops
2. **No group chat** - Only 1-on-1 conversations
3. **No file transfer** - Text messages only
4. **No mobile apps** - Desktop only (Python required)
5. **No message sync** - Each device has separate identity
6. **Rate limiting** - Max 100 messages per 60 seconds per peer
7. **No voice/video** - Text only
8. **Manual fingerprint verification** - Not automated

### Best Practices

1. **Always verify fingerprints** when connecting to new peer
2. **Use strong passphrases** (12+ characters)
3. **Keep software updated** for security fixes
4. **Regular backups** of `.secure_chat` directory (encrypted)
5. **Restart periodically** for best performance
6. **Disconnect inactive peers** to free resources
7. **Monitor logs** for security events
8. **Use VPN** for internet connections if possible
9. **Test locally first** before internet connections
10. **Document your setup** for future reference

### Emergency Procedures

#### Complete Reset (Loses All Data)
```bash
# Backup first (optional)
cp -r ~/.secure_chat ~/secure_chat_backup

# Remove all data
rm -rf ~/.secure_chat

# Restart application to create fresh identity
python3 gui.py
```

#### Export Messages Before Reset
```bash
# Messages are encrypted, so export requires passphrase
# Currently no export tool - future enhancement
# For now, screenshot important messages
```

#### Recover from Corrupted State
```bash
# Stop application
pkill -f gui.py

# Check what's corrupted
cd ~/.secure_chat
ls -lah

# If identity corrupted, remove and recreate
rm identity.enc
# Next start will create new identity

# If database corrupted
rm messages.db
# Next start will create new database
```

---

## Quick Reference

### Status Indicators
- 🟢 Green circle: Peer connected
- 💬 Chat bubble: Conversation selected
- 🔐 Lock: Encryption active (always)
- ⚠️ Warning: Security alert

### Keyboard Shortcuts
- Enter: Send message
- Ctrl+C: Copy (in text areas)
- Ctrl+V: Paste (in input)

### File Locations
- Identity: `~/.secure_chat/identity.enc`
- Messages: `~/.secure_chat/messages.db`
- Logs: `~/.secure_chat/chat_YYYYMMDD.log`

### Port Information
- Default: 8765
- Protocol: TCP
- Direction: Both inbound and outbound

---

**Still having issues?** Create a detailed GitHub issue with:
- Problem description
- Steps to reproduce
- System information
- Error messages
- Test results
