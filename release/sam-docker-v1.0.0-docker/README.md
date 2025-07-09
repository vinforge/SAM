# 🐳 SAM Docker Release v1.0.0-docker

**SAM (Secure AI Memory)** - Advanced AI assistant with human-like conceptual understanding, now available as a containerized application.

## 🚀 Quick Start

### Prerequisites
- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **4GB RAM** minimum (8GB+ recommended)
- **10GB+ free disk space**

### One-Command Deployment

#### **Windows**
```batch
# Run the Windows batch file
quick_start.bat

# OR use PowerShell/WSL
./quick_start.sh
```

#### **Linux/macOS**
```bash
# Start SAM
./quick_start.sh
```

**Access SAM at: http://localhost:8502**

## 📦 What's Included

- **Complete SAM Stack**: AI assistant with memory capabilities
- **Vector Database**: ChromaDB for semantic search
- **Redis Cache**: Fast session management
- **Health Monitoring**: Built-in health checks
- **Management Tools**: Comprehensive management script

## 🏗️ Architecture

Multi-container stack:
- **SAM Main App**: Streamlit application (Port 8502)
- **Memory Center**: Advanced memory management (Port 8501)
- **Setup Interface**: First-time setup (Port 8503)
- **Redis**: Session and cache management (Port 6379)
- **ChromaDB**: Vector database (Port 8000)

## 🛠️ Management

Use the included `manage_sam.sh` script:

```bash
./manage_sam.sh start          # Start services
./manage_sam.sh stop           # Stop services
./manage_sam.sh status         # Check status
./manage_sam.sh logs           # View logs
./manage_sam.sh backup         # Create backup
./manage_sam.sh update         # Update SAM
```

## 💾 Data Persistence

All data is preserved in Docker volumes:
- Application data and documents
- Memory store and knowledge base
- Security configurations
- Logs and cache

## 📚 Documentation

- **Complete Guide**: `DOCKER_DEPLOYMENT_GUIDE.md`
- **Docker README**: `README_DOCKER.md`
- **GitHub**: https://github.com/forge-1825/SAM

## 🔒 Security

- Non-root container execution
- Isolated network configuration
- Encrypted data storage
- Secure session management

## 📞 Support

- **Issues**: https://github.com/forge-1825/SAM/issues
- **Documentation**: https://github.com/forge-1825/SAM
- **Email**: vin@forge1825.net

## 📄 License

MIT License - See LICENSE file for details.

---

**Version**: v1.0.0-docker  
**Build Date**: 2025-07-09T22:41:28Z  
**Git Commit**: f4c0119

**Ready to experience the future of AI assistance!** 🚀
