# 🔐 SAM Encryption Setup Guide

## Quick Start

**For new users:**
```bash
python setup.py
# Choose option 4: Encryption Only Setup
# Follow the prompts to create your master password
```

**For existing installations:**
```bash
python setup_encryption.py
# Choose option 1 to test existing password
# Or option 2 to reset encryption
```

---

## Understanding SAM's Encryption

### 🔒 **What Gets Encrypted**
- All memory data and conversations
- User preferences and settings
- API keys and sensitive configuration
- Session data and authentication tokens

### 🛡️ **Security Features**
- **AES-256-GCM** authenticated encryption
- **Argon2id** key derivation (industry standard)
- **Session-based** security with automatic timeout
- **Zero-knowledge** architecture (passwords never stored)

---

## Setup Scenarios

### 🆕 **Scenario 1: First-Time Setup**

**When:** You're installing SAM for the first time

**Process:**
1. Run `python setup.py` and choose option 4
2. System detects no existing encryption
3. Prompts you to create a master password
4. Generates encryption keys automatically
5. Initializes secure storage

**Result:** ✅ Ready to use SAM with encryption

---

### 🔄 **Scenario 2: Existing Installation**

**When:** SAM is already installed but you want to set up encryption

**Process:**
1. Run `python setup_encryption.py`
2. System detects existing keystore
3. Offers three options:
   - **Test existing password** (if you know it)
   - **Reset encryption** (if you forgot password)
   - **Skip setup** (if you want to exit)

**Choose Option 1 if:**
- You know your master password
- You want to verify encryption is working
- This is a shared/team installation

**Choose Option 2 if:**
- You forgot your master password
- Previous setup was incomplete
- You want to start fresh

---

### 🔧 **Scenario 3: Troubleshooting**

**When:** Encryption isn't working properly

**Quick Diagnosis:**
```bash
python test_encryption_setup.py
```

**Common Issues:**

#### **"Module not found" errors**
```bash
pip install -r requirements.txt
```

#### **"Keystore locked" errors**
- You need to enter your master password
- Run SAM and authenticate when prompted

#### **"Authentication failed" errors**
- Wrong master password
- Consider resetting encryption (option 2)

#### **"Setup required" but you have a keystore**
- Keystore may be corrupted
- Reset encryption to fix

---

## Master Password Guidelines

### ✅ **Good Passwords**
- At least 12 characters long
- Mix of letters, numbers, symbols
- Unique to SAM (don't reuse)
- Something you'll remember

### ❌ **Avoid**
- Common words or phrases
- Personal information (birthdays, names)
- Passwords used elsewhere
- Anything under 8 characters

### 💡 **Tips**
- Use a passphrase: "Coffee!Helps@Me#Think2024"
- Consider a password manager
- Write it down securely (offline)
- Test it immediately after creation

---

## Command Reference

### **Setup Commands**
```bash
# Interactive setup menu
python setup.py

# Direct encryption setup
python setup_encryption.py

# Test encryption status
python test_encryption_setup.py

# Start SAM with encryption
python start_sam_secure.py --mode full
```

### **Troubleshooting Commands**
```bash
# Check if files exist
ls -la security/

# Verify Python dependencies
pip list | grep -E "(cryptography|argon2)"

# Check SAM directory
pwd  # Should be in SAM root directory
```

---

## Security States Explained

### 🆕 **SETUP_REQUIRED**
- No encryption configured
- Need to create master password
- Run encryption setup

### 🔒 **LOCKED**
- Encryption configured but not authenticated
- Need to enter master password
- Normal state when starting SAM

### ✅ **AUTHENTICATED**
- Successfully entered master password
- Encryption active and working
- Ready to use SAM securely

### ❌ **ERROR**
- Configuration problem detected
- May need to reset encryption
- Check logs for details

---

## Advanced Options

### **Reset Encryption**
⚠️ **Warning:** This deletes all encrypted data!

```bash
python setup_encryption.py
# Choose option 2: Reset encryption
# Type 'RESET' to confirm
# Creates backup of old keystore
# Prompts for new master password
```

### **Backup Keystore**
```bash
# Manual backup
cp security/keystore.json security/keystore_backup_$(date +%Y%m%d).json

# Automatic backups are created during reset
ls security/keystore_backup_*.json
```

### **Multiple Users**
Each user should:
1. Know the shared master password, OR
2. Reset encryption for their own password
3. Understand that reset deletes previous data

---

## FAQ

### **Q: I forgot my master password. What do I do?**
A: Run `python setup_encryption.py`, choose option 2 to reset. This will delete encrypted data but create a backup.

### **Q: Can I change my master password?**
A: Currently, you need to reset encryption (option 2) to change passwords. This creates a new keystore.

### **Q: Is my data safe?**
A: Yes! SAM uses military-grade AES-256-GCM encryption with Argon2id key derivation. Your master password is never stored.

### **Q: What happens if I lose the keystore file?**
A: You'll need to reset encryption. The keystore contains your encrypted keys, so losing it means losing access to encrypted data.

### **Q: Can I use SAM without encryption?**
A: Yes, but it's not recommended. Run `python start_sam.py` instead of the secure version.

### **Q: How do I know encryption is working?**
A: Run `python test_encryption_setup.py` to verify all components are working correctly.

---

## Support

If you encounter issues:

1. **Run diagnostics:** `python test_encryption_setup.py`
2. **Check logs:** Look in `logs/` directory
3. **Reset if needed:** Use option 2 in setup
4. **Verify installation:** Ensure you're in SAM directory

**Remember:** Your master password is the key to your encrypted data. Keep it safe! 🔐
