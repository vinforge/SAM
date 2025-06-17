# 🔐 SAM Encryption - Quick Setup Card

**5-Minute Setup Guide for New Users**

---

## 🚀 **Super Quick Start**

```bash
# 1. Navigate to SAM directory
cd SAM

# 2. Launch SAM with security
python start_sam_secure.py --mode full

# 3. Follow the setup wizard
# 4. Access SAM at http://localhost:8502
```

---

## 🔑 **Master Password Creation**

### **When SAM Starts for the First Time:**
```
🔐 SAM Secure Enclave Setup
───────────────────────────

🔑 Create Master Password
Password: ****************
Confirm:  ****************
```

### **Password Requirements:**
- ✅ **8+ characters** (12+ recommended)
- ✅ **Mix of letters, numbers, symbols**
- ✅ **Unique password** (don't reuse)
- ⚠️ **Cannot be recovered** - remember it!

### **Good Password Examples:**
```
MyS3cur3P@ssw0rd!2024
Tr0ub4dor&3_SAM_Key
C0ff33&Cr3am_Encrypt!
```

---

## 🔒 **What Gets Encrypted**

✅ **All conversations** and chat history  
✅ **Uploaded documents** and content  
✅ **Memory entries** and metadata  
✅ **User preferences** and settings  
✅ **Vector embeddings** metadata  

---

## 🌐 **Access Points After Setup**

| Interface | URL | Purpose |
|-----------|-----|---------|
| **Secure Chat** | http://localhost:8502 | Primary interface |
| **Memory Center** | http://localhost:8501 | Memory management |
| **Web UI** | http://localhost:5001 | Alternative interface |

---

## 🛡️ **Security Features**

- **AES-256-GCM**: Military-grade encryption
- **Argon2id**: Enterprise password protection
- **Zero-Knowledge**: Password never stored
- **Local Processing**: Data never leaves your device
- **Auto-Lock**: Sessions timeout after 1 hour

---

## 🆘 **Quick Troubleshooting**

### **First Run Issues:**
```bash
# Missing dependencies
pip install argon2-cffi cryptography streamlit

# Permission errors
chmod 700 security/
```

### **Password Issues:**
- ❌ **Wrong password**: Check caps lock, type carefully
- ❌ **Forgot password**: No recovery - all data lost
- ✅ **Use password manager** to store safely

### **Reset Everything (LOSES ALL DATA):**
```bash
rm security/keystore.json
python start_sam_secure.py --mode full
```

---

## 📋 **Migration from Existing SAM**

If you have SAM without encryption:

```bash
# Migrate existing data to encrypted format
python start_sam_secure.py --mode migrate
```

**Migration Process:**
1. Creates backup of existing data
2. Prompts for master password
3. Encrypts all existing content
4. Verifies migration success

---

## ✅ **Verification Checklist**

After setup, verify everything works:

- [ ] Can access http://localhost:8502
- [ ] Master password unlocks SAM
- [ ] Can upload and chat with documents
- [ ] Session locks after timeout
- [ ] Can unlock with master password
- [ ] Keystore file exists: `security/keystore.json`

---

## 🔄 **Daily Usage**

### **Starting SAM:**
```bash
python start_sam_secure.py --mode full
```

### **First Access Each Day:**
1. Go to http://localhost:8502
2. Enter your master password
3. Start chatting securely!

### **Session Management:**
- Sessions auto-lock after 1 hour
- Manual lock: Click lock button in interface
- Unlock: Enter master password again

---

## 📞 **Need Help?**

- 📖 **Full Guide**: `docs/ENCRYPTION_SETUP_GUIDE.md`
- 🔧 **Installation**: `docs/README_SECURE_INSTALLATION.md`
- 🆘 **Troubleshooting**: Check `logs/security.log`
- 🐛 **Issues**: Report with error details

---

## ⚠️ **Critical Reminders**

1. **🔑 REMEMBER YOUR MASTER PASSWORD** - No recovery possible
2. **💾 Backup important documents** separately 
3. **🔒 Use a password manager** to store your master password
4. **🏠 Keep SAM local** - don't expose to internet without VPN
5. **🔄 Regular backups** of encrypted data recommended

---

**🎉 You're ready to use SAM securely!**

Your conversations, documents, and memories are now protected with enterprise-grade encryption. Enjoy your private AI assistant!
