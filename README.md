# 🧠 SAM (Secure AI Memory) - Community Edition

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)

**SAM** is an advanced AI assistant with secure memory capabilities, designed to provide personalized, context-aware interactions while maintaining enterprise-grade security and privacy.

SAM is an open-source AI assistant designed to provide intelligent conversations while maintaining complete privacy. Everything runs locally on your computer - no data is sent to external servers.

## ✨ Key Features

### 🧠 **Advanced Memory System (Phase 3 Enhanced)**
- **Hybrid Search & Ranking:** Multi-strategy search with configurable weights
- **Persistent Memory:** Remembers conversations across sessions
- **Smart Document Learning:** Learns from uploaded documents with enhanced processing
- **Real-time Memory Management:** Interactive filtering and analytics dashboard

### 📄 **Intelligent Document Processing**
- **Enhanced PDF Analysis:** Advanced content extraction and structure preservation
- **Multi-format Support:** PDF, text, and document intelligence
- **Source-specific Queries:** Search within specific documents or sources
- **Intelligent Summarization:** Context-aware document synthesis

### 💭 **Transparent AI Reasoning**
- **SAM's Thoughts Toggle:** View internal reasoning processes
- **Enhanced Citations:** Granular source attribution with confidence indicators
- **Decision Transparency:** Understand how conclusions are reached
- **Quality Metrics:** Real-time confidence and transparency scoring

### 🔍 **Advanced Search & Analytics (Phase 3.2.3)**
- **Real-time Search:** Search as you type with live results
- **Multi-mode Filtering:** Enhanced Hybrid, Semantic, Keyword, Recent strategies
- **Source Analysis Dashboard:** Visual metrics and quality indicators
- **Interactive Configuration:** Real-time weight adjustment and optimization

### 🔒 **Privacy First**
- **100% Local Processing:** No cloud dependencies or data transmission
- **Open Source:** Inspect and modify all code
- **No Telemetry:** Zero data collection or tracking
- **Secure by Design:** Your data never leaves your computer

### 🌐 **Professional Interface**
- **Dual-Interface Design:** Chat (5001) and Memory Control Center (8501)
- **Memory Management Dashboard:** Advanced filtering and analytics
- **Cross-platform Support:** Windows, macOS, Linux
- **Mobile-responsive Design:** Access from any device

## 🚀 Quick Start

### 1. Install SAM
```bash
# Clone the repository
git clone http://172.16.20.246:3000/Forge/SAM.git
cd SAM

# Run the installer
python install.py
```

### 2. Start SAM
```bash
python start_sam.py
```

### 3. Access SAM
- **Chat Interface**: http://localhost:5001
- **Memory Control**: http://localhost:8501

That's it! SAM will automatically open in your browser.

## 🚀 Phase 3 Enhancements (2025)

SAM has been significantly enhanced with Phase 3 features that transform it into a production-ready AI assistant:

### **Phase 3.2.1: Enhanced Search & Ranking Engine**
- **Hybrid Search:** Combines semantic similarity, recency, and confidence scoring
- **Configurable Weights:** Real-time adjustment of ranking factors
- **Multi-Strategy Search:** Semantic, keyword, recency, and confidence-based approaches
- **Performance Analytics:** Detailed scoring breakdown and transparency metrics

### **Phase 3.2.2: Citation System Refactoring**
- **Direct Metadata Access:** Eliminated legacy lookups for improved performance
- **Enhanced Citations:** Confidence indicators and granular location metadata
- **Rich Formatting:** Visual confidence badges and source transparency
- **Backward Compatibility:** Seamless integration with existing systems

### **Phase 3.2.3: Memory Control Center Enhancement**
- **Real-time Filtering:** Advanced search with live result updates
- **Source Analysis Dashboard:** Visual metrics and quality indicators
- **Interactive Configuration:** Live weight adjustment and optimization
- **Enhanced UI:** Professional interface with progressive disclosure

## 📋 Requirements

- **Python 3.8+** (Python 3.9+ recommended)
- **4GB+ RAM** (8GB+ recommended for better performance)
- **2GB+ free disk space**
- **Internet connection** (for initial model download)

## 🎯 What Can SAM Do?

### 💬 **Enhanced Chat & Learning**
- **Natural Conversations:** Intelligent responses with context awareness
- **Transparent Reasoning:** Toggle "SAM's Thoughts" to see decision processes
- **Source Attribution:** Every response includes confidence-scored citations
- **Continuous Learning:** Builds knowledge from every interaction

### 📊 **Advanced Document Analysis**
- **Multi-format Processing:** PDF, text, and structured document support
- **Intelligent Questioning:** Ask complex questions about document content
- **Enhanced Summarization:** Context-aware synthesis with source transparency
- **Knowledge Base Building:** Searchable, categorized document repository

### 🎛️ **Professional Memory Management (Phase 3.2.3)**
- **Advanced Search Interface:** Real-time filtering with multiple strategies
- **Source Analysis Dashboard:** Visual analytics and quality metrics
- **Interactive Configuration:** Real-time weight adjustment and optimization
- **Memory Analytics:** Comprehensive statistics and performance tracking

### 🔍 **Intelligent Search & Discovery**
- **Hybrid Search Engine:** Combines semantic, keyword, and recency-based search
- **Source-specific Queries:** Target specific documents or content types
- **Similar Content Discovery:** Find related memories with one click
- **Quality-based Filtering:** Filter by confidence, recency, and source quality

## 🔧 Configuration

SAM uses a simple JSON configuration file at `config/sam_config.json`:

```json
{
  "version": "1.0.0-beta",
  "model": {
    "provider": "ollama",
    "model_name": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M",
    "api_url": "http://localhost:11434"
  },
  "ui": {
    "chat_port": 5001,
    "memory_ui_port": 8501,
    "host": "0.0.0.0",
    "auto_open_browser": true
  },
  "memory": {
    "max_memories": 10000,
    "backend": "simple",
    "storage_dir": "memory_store"
  },
  "features": {
    "show_thoughts": true,
    "document_upload": true,
    "memory_management": true
  }
}
```

### Key Settings
- **Ports**: Change `chat_port` and `memory_ui_port` if needed
- **Memory**: Adjust `max_memories` based on your needs
- **Features**: Enable/disable specific functionality
- **Model**: Configure different AI models (advanced users)

## 🆘 Troubleshooting

### Common Issues

**SAM won't start:**
- Check that Ollama is installed: `ollama --version`
- Ensure the model is downloaded: `ollama list`
- Check logs: `tail -f logs/sam.log`

**Can't access the web interface:**
- Verify the port isn't in use: `lsof -i :5001`
- Try a different port in `config/sam_config.json`
- Check firewall settings

**Memory issues:**
- Restart SAM completely
- Clear old memories from the Memory Control Center
- Check available disk space

**Document upload problems:**
- Ensure PDFs are not password-protected
- Check file size (large files may take time to process)
- Verify sufficient disk space

### Getting Help
1. **Check the logs**: `logs/sam.log` contains detailed error information
2. **System status**: Visit http://localhost:5001/health
3. **Read the setup guide**: See `SETUP_GUIDE.md` for detailed instructions
4. **Reset if needed**: Delete `memory_store/` and `config/` to start fresh

## 🔒 Privacy & Security

SAM is built with privacy as a core principle:

- **Local Processing**: All AI operations happen on your computer
- **No Cloud Dependencies**: No data sent to external servers
- **Open Source**: Full transparency - inspect and modify the code
- **Your Data Stays Yours**: Conversations and documents remain on your device

## 📊 System Architecture

```
SAM Community Edition/
├── start_sam.py           # Main launcher
├── launch_web_ui.py       # Web interface launcher
├── install.py             # Installation script
├── config/                # Configuration files
├── web_ui/               # Web interface
├── ui/                   # User interface components
├── memory/               # Memory management
├── multimodal/           # Document processing
├── logs/                 # Application logs
└── memory_store/         # Stored memories and documents
```

## 🚀 Advanced Usage

### Custom Models
SAM supports different AI models through Ollama. To use a different model:

1. Download the model: `ollama pull model-name`
2. Update `config/sam_config.json` with the new model name
3. Restart SAM

### Memory Backends
- **Simple**: Default, good for most users
- **FAISS**: Better performance for large memory stores
- **Chroma**: Advanced features and persistence

### API Access
SAM provides REST API endpoints for integration:
- `GET /health` - System health check
- `POST /chat` - Send messages to SAM
- `GET /memories` - Retrieve stored memories

## 🔄 Updates

To update SAM:
1. **Backup**: Export memories from Memory Control Center
2. **Download**: Get the latest version
3. **Install**: Run `python install.py`
4. **Restore**: Import your backed-up memories

## 📞 Support

- **Documentation**: `SETUP_GUIDE.md` for detailed setup instructions
- **Deployment**: `DEPLOYMENT.md` for production deployment
- **Logs**: Check `logs/sam.log` for troubleshooting
- **Community**: Join our community for help and discussions

---

**Welcome to SAM Community Edition Beta!** 🎉

Start by uploading a document and asking SAM questions about it. Experience the power of local AI with complete privacy.
