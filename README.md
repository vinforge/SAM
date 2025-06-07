# SAM Community Edition Beta

**Smart Assistant Memory** - A privacy-focused AI assistant that learns and remembers.

SAM is an open-source AI assistant designed to provide intelligent conversations while maintaining complete privacy. Everything runs locally on your computer - no data is sent to external servers.

## ✨ Key Features

### 🧠 **Persistent Memory**
- Remembers conversations across sessions
- Learns from uploaded documents
- Builds knowledge over time
- Smart memory management

### 📄 **Document Intelligence**
- Upload PDF documents for analysis
- Automatic content extraction and indexing
- Ask questions about your documents
- Intelligent document summarization

### 💭 **Transparent Thinking**
- See how SAM reasons through problems
- Toggle "SAM's Thoughts" to view internal reasoning
- Understand the AI's decision-making process
- Build trust through transparency

### 🔒 **Privacy First**
- 100% local processing - no cloud dependencies
- Your data never leaves your computer
- Open source - inspect and modify the code
- No telemetry or data collection

### 🌐 **Easy to Use**
- Clean web interface
- Memory management dashboard
- Simple installation process
- Cross-platform support

## 🚀 Quick Start

### 1. Install SAM
```bash
# Download SAM (or clone the repository)
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

## 📋 Requirements

- **Python 3.8+** (Python 3.9+ recommended)
- **4GB+ RAM** (8GB+ recommended for better performance)
- **2GB+ free disk space**
- **Internet connection** (for initial model download)

## 🎯 What Can SAM Do?

### Chat & Learn
- Have natural conversations with an AI assistant
- Ask questions and get thoughtful responses
- See SAM's reasoning process with "Thoughts" toggle

### Document Analysis
- Upload PDF documents
- Ask questions about document content
- Get summaries and insights
- Build a searchable knowledge base

### Memory Management
- Browse all stored memories
- Search through conversation history
- Manage document uploads
- View system statistics

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
