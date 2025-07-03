# 🚀 SAM Setup Options Guide

Complete overview of all available setup methods for SAM (Secure AI Memory).

## 📋 **Quick Reference**

| Method | Time | Difficulty | Best For |
|--------|------|------------|----------|
| Interactive Script | 10-15 min | Beginner | New users, guided setup |
| Quick Setup | 5 min | Easy | Fast deployment, defaults |
| Manual Installation | 20-30 min | Advanced | Custom configuration |
| Encryption Only | 5 min | Easy | Existing installations |

## 🎯 **Option 1: Interactive Script (Recommended)**

### **What it does:**
- Guided setup wizard with step-by-step instructions
- Automatic dependency detection and installation
- Interactive encryption setup with password validation
- System optimization and configuration

### **How to run:**
```bash
python setup.py
# Choose option 1
```

### **Perfect for:**
- First-time SAM users
- Users who want guided installation
- Anyone who prefers step-by-step instructions

## ⚡ **Option 2: Quick Setup**

### **What it does:**
- Fast installation with minimal prompts
- Default configuration (customizable later)
- Basic encryption setup
- Automatic dependency installation

### **How to run:**
```bash
python setup.py
# Choose option 2
```

### **Perfect for:**
- Experienced users
- Quick deployments
- Testing environments

## 🔧 **Option 3: Manual Installation**

### **What it does:**
- Complete control over all settings
- Custom configuration options
- Advanced security settings
- Step-by-step manual process

### **How to run:**
```bash
python setup.py
# Choose option 3
```

### **Steps included:**
1. Install dependencies manually
2. Install Ollama AI model
3. Create directories
4. Setup encryption
5. Launch SAM

### **Perfect for:**
- Advanced users
- Custom deployments
- Specific requirements

## 🔐 **Option 4: Encryption Only Setup**

### **What it does:**
- Adds enterprise-grade encryption to existing SAM
- Master password creation with validation
- Secure storage initialization

### **How to run:**
```bash
python setup.py
# Choose option 4

# Or directly:
python setup_encryption.py
```

### **Perfect for:**
- Existing SAM installations
- Adding security to current setup
- Upgrading to secure version

## 📖 **Option 5: View Documentation**

### **What it provides:**
- Complete setup guides
- Troubleshooting information
- Advanced configuration options
- Links to online resources

## 🛠️ **Alternative Setup Methods**

### **Direct Installation Scripts:**

#### **Interactive Setup:**
```bash
python interactive_setup.py
```

#### **Quick Installation:**
```bash
python install_sam.py
```

#### **Encryption Setup:**
```bash
python setup_encryption.py
```

#### **Direct Launch:**
```bash
python start_sam_secure.py --mode full
```

## 📋 **System Requirements**

### **Minimum Requirements:**
- Python 3.8 or higher
- 4GB RAM (8GB+ recommended)
- 2GB free disk space
- Internet connection (for dependencies)

### **Recommended:**
- Python 3.10+
- 8GB+ RAM
- 5GB+ free disk space
- Ollama installed for AI features

## 🔧 **Troubleshooting**

### **Common Issues:**

#### **Missing requirements.txt:**
```bash
# Create basic requirements file
pip install streamlit flask sentence-transformers requests beautifulsoup4 PyPDF2 python-docx psutil cryptography argon2-cffi chromadb pandas numpy
```

#### **Interactive setup not found:**
```bash
# Ensure you're in SAM directory
ls interactive_setup.py

# If missing, download from repository
```

#### **Dependency installation fails:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install dependencies manually
pip install -r requirements.txt
```

#### **Ollama not found:**
- Visit: https://ollama.ai/download
- Install for your platform
- Run: `ollama pull hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M`

## 🚀 **After Installation**

### **Starting SAM:**
```bash
python start_sam_secure.py --mode full
```

### **Access Points:**
- **Secure Chat:** http://localhost:8502
- **Memory Center:** http://localhost:8501  
- **Standard Chat:** http://localhost:5001

### **First Time Setup:**
1. Create master password when prompted
2. Wait for encryption setup to complete
3. Access SAM through secure interface
4. Upload documents and start chatting!

## 📚 **Additional Resources**

- **Main Documentation:** `docs/README.md`
- **Encryption Guide:** `docs/ENCRYPTION_SETUP_GUIDE.md`
- **Deployment Guide:** `docs/DEPLOYMENT.md`
- **Contributing:** `docs/CONTRIBUTING.md`

## 💡 **Tips**

- Start with **Interactive Script** if you're new to SAM
- Use **Quick Setup** for fast deployments
- Choose **Manual Installation** for custom configurations
- Run **Encryption Only** to secure existing installations

---

**Need help?** Check the documentation in the `docs/` folder or visit the GitHub repository for support.
