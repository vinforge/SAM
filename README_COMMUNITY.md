# 🧠 SAM (Secure AI Memory) - Community Edition

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)

**SAM** is an advanced AI assistant with secure memory capabilities, designed to provide personalized, context-aware interactions while maintaining enterprise-grade security and privacy.

## ✨ Key Features

### 🔒 **Enterprise Security**
- **End-to-end encryption** for all stored data
- **Zero-knowledge architecture** - your data stays private
- **Secure memory storage** with encrypted ChromaDB backend
- **Session-based security** with automatic lockout

### 🧠 **Advanced Memory System**
- **Semantic search** across all your documents and conversations
- **Intelligent document processing** with PDF, DOCX, TXT support
- **Context-aware responses** based on your personal knowledge base
- **Memory ranking** with recency, relevance, and confidence scoring

### 🚀 **Multiple Interfaces**
- **Secure Web UI** (Flask-based) - Main chat interface
- **Memory Control Center** (Streamlit) - Memory management
- **Secure Document App** (Streamlit) - Document upload and search
- **CLI Tools** - Command-line memory management

### 🤖 **AI Integration**
- **Local LLM support** via Ollama (privacy-first)
- **Embedding models** for semantic understanding
- **Multimodal processing** for various document types
- **Reasoning frameworks** for intelligent responses

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- 4GB+ RAM recommended
- 2GB+ free disk space

### Installation

#### Option 1: Automated Installation (Recommended)
```bash
# Clone the repository
git clone https://github.com/your-org/SAM.git
cd SAM

# Run the installer
python install.py
```

#### Option 2: Manual Installation
```bash
# Clone and setup
git clone https://github.com/your-org/SAM.git
cd SAM

# Install dependencies
pip install -r requirements.txt

# Initialize SAM
python start_sam.py --setup
```

### First Run

1. **Start SAM**:
   ```bash
   python start_sam_secure.py --mode full
   ```

2. **Access the interfaces**:
   - **Main Chat**: http://localhost:5001
   - **Memory Center**: http://localhost:8501
   - **Document Upload**: http://localhost:8502

3. **Setup Security**:
   - Create a master password when prompted
   - Your data will be encrypted with this password
   - **Important**: Store your password safely - it cannot be recovered!

## 📖 Usage Guide

### Document Upload
1. Go to the **Secure Document App** (port 8502)
2. Upload PDF, DOCX, or TXT files
3. Files are automatically processed and encrypted
4. Search your documents using natural language

### Chat Interface
1. Use the **Main Chat** interface (port 5001)
2. Ask questions about your uploaded documents
3. SAM will provide context-aware responses
4. All conversations are encrypted and stored securely

### Memory Management
1. Access the **Memory Control Center** (port 8501)
2. Browse, search, and manage your memories
3. Export/import memory collections
4. View memory statistics and insights

## 🔧 Configuration

### Local LLM Setup (Recommended)
SAM works best with a local LLM for privacy:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download a model (example)
ollama pull llama2:7b

# Configure SAM to use your model
# Edit config/sam_config.json
```

### Environment Variables
```bash
# Optional: Set custom ports
export SAM_WEB_PORT=5001
export SAM_MEMORY_PORT=8501
export SAM_SECURE_PORT=8502

# Optional: Set custom data directory
export SAM_DATA_DIR=/path/to/your/data
```

## 🛡️ Security Features

- **AES-256-GCM encryption** for all stored data
- **Argon2 key derivation** for password security
- **In-memory session keys** (never stored on disk)
- **Encrypted metadata** with selective field encryption
- **Secure ChromaDB integration** with encrypted collections

## 📁 Project Structure

```
SAM/
├── 🚀 start_sam_secure.py     # Main launcher
├── 🌐 secure_streamlit_app.py # Document interface
├── 📋 requirements.txt        # Dependencies
├── 📖 README.md              # This file
├── 🔒 security/              # Security modules
├── 🧠 memory/                # Memory management
├── 🔧 utils/                 # Utilities
├── 🎨 ui/                    # User interfaces
├── ⚙️ config/                # Configuration
└── 📚 docs/                  # Documentation
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone for development
git clone https://github.com/your-org/SAM.git
cd SAM

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/SAM/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/SAM/discussions)

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/) and [Flask](https://flask.palletsprojects.com/)
- Powered by [ChromaDB](https://www.trychroma.com/) and [FAISS](https://faiss.ai/)
- Security by [cryptography](https://cryptography.io/) library
- AI integration via [Ollama](https://ollama.ai/)

---

**SAM - Your Secure AI Memory Assistant** 🧠🔒✨
