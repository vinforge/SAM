#!/usr/bin/env python3
"""
SAM Community Edition - Beta Release Preparation Script
Prepare SAM for community beta release by cleaning up development files and organizing for production.
"""

import os
import sys
import glob
import shutil
import logging
import json
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cleanup_development_files():
    """Remove development and debug files for beta release."""
    logger.info("🧹 Cleaning up development files...")
    
    # Files and directories to remove for beta release
    cleanup_targets = [
        # Development cache and compiled files
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".pytest_cache",

        # Personal/development directories
        "MyStuff",
        "backups",
        "temp_uploads",
        "uploads",

        # Development logs and databases
        "curiosity.log",
        "enrichment.log",
        "logs/curiosity_signals.db",
        "logs/retrieval_logs.db",
        "logs/sam_knowledge.db",
        "logs/sam_launcher.log",
        "logs/bulk_ingest.log",
        "web_ui/curiosity.log",

        # Debug and test files
        "test_*.py",
        "debug_*.py",
        "check_*.py",
        "process_*.py",
        "fix_*.py",
        "demo_*.py",
        "clear_*.py",
        "cleanup_*.py",

        # Development documentation
        "steps*.md",
        "SPRINT_*.md",
        "DIAGNOSTIC_*.md",
        "KNOWLEDGE_*.md",
        "LONGBIOBENCH_*.md",
        "MEMORY_*.md",
        "test_*.md",
        "PHASE*_TESTING_GUIDE.md",
        "BETA_RELEASE_CHECKLIST.md",
        "DEPLOYMENT_CHECKLIST.md",

        # Development data and logs
        "execution_logs",
        "task_run_reports",
        "demo_memory",
        "test_memory",
        "test_compat",
        "test_data",

        # User data (will be recreated on first run)
        "memory_store/*.json",
        "memory_store/*.db",
        "multimodal_output",
        "data/uploads/*",
        "data/documents/*",
        "data/vector_store/*",
        "data/ingestion_state.db",
        "web_ui/uploads/*",
        "web_ui/data/*",
        "web_ui/memory_store/*",
        "web_ui/memory_store_backup",
        "web_ui/multimodal_output/*",
        "web_ui/mem_*.json",
        "streamlit_data",
        "chroma_db",
        "vector_store/enriched_chunks/*",

        # Development configs
        "agent_manager_config.json",
        "swarm_config.json",
        "task_manager.json",
        "tool_registry.json",
        "tool_scorecard.json",
        "user_feedback.json",
        "remote_agents.yaml",
        "search_index.json",
        "memory_store.json",
        "config/collab_key.json",
        "custom_tools",

        # Development scripts
        "start_sprint*.py",
        "streamlit_*.py",
        "migrate_*.py",
        "security_integration_example.py",

        # Development prompts and configs
        "system_prompt/curious_analyst_prompt.txt",
        "sam_tool_augmented_prompt.txt",

        # Docker files (provide separate Docker setup)
        "Dockerfile",
        "docker-compose.yml",
        "sam.service",

        # Development utilities
        "enhanced_*.py",
        "gpu_*.py",
        "domain_*.py",
        "knowledge_navigator.py",
        "cli_tools.py",
        "main.py",  # Keep start_sam.py and launch_web_ui.py instead

        # Installer artifacts
        "sam-installer",
    ]
    
    # Keep these essential files
    essential_files = [
        "README.md",
        "requirements.txt",
        "launch_web_ui.py",        # Main web UI launcher
        "start_sam.py",            # Main SAM launcher
        "start_sam_secure.py",     # Secure SAM launcher
        "secure_streamlit_app.py", # Secure Streamlit interface
        "install.py",              # Installation script
        "install_sam.py",          # Alternative installer
        "install.sh",              # Shell installer
        "install.bat",             # Windows installer
        "start_sam.sh",            # Shell launcher
        "start_sam.bat",           # Windows launcher
        "SAM-whitepaper.md",
        "DEPLOYMENT.md",
        "README_SECURE_INSTALLATION.md",
        "SETUP_GUIDE.md",
        "Makefile",
        ".gitignore",
        "LICENSE",
    ]
    
    removed_count = 0
    
    # Remove target files and directories
    for target in cleanup_targets:
        if target in essential_files:
            logger.info(f"⚠️  Skipping essential file: {target}")
            continue
            
        # Handle glob patterns
        if "*" in target:
            matches = glob.glob(target, recursive=True)
            for match in matches:
                if os.path.basename(match) in essential_files:
                    logger.info(f"⚠️  Skipping essential file: {match}")
                    continue
                try:
                    if os.path.isdir(match):
                        shutil.rmtree(match)
                        logger.info(f"🗑️  Removed directory: {match}")
                    else:
                        os.remove(match)
                        logger.info(f"🗑️  Removed file: {match}")
                    removed_count += 1
                except Exception as e:
                    logger.warning(f"⚠️  Could not remove {match}: {e}")
        else:
            # Handle direct paths
            if os.path.exists(target):
                try:
                    if os.path.isdir(target):
                        shutil.rmtree(target)
                        logger.info(f"🗑️  Removed directory: {target}")
                    else:
                        os.remove(target)
                        logger.info(f"🗑️  Removed file: {target}")
                    removed_count += 1
                except Exception as e:
                    logger.warning(f"⚠️  Could not remove {target}: {e}")
    
    logger.info(f"✅ Cleanup complete! Removed {removed_count} files/directories")
    return removed_count

def create_production_directories():
    """Create essential directories for production."""
    logger.info("📁 Creating production directories...")
    
    essential_dirs = [
        "logs",
        "config",
        "data/uploads", 
        "data/documents",
        "data/vector_store",
        "memory_store",
        "multimodal_output",
        "web_ui/uploads",
        "web_ui/data",
        "web_ui/memory_store",
        "web_ui/multimodal_output",
        "models/embeddings",
        "vector_store/enriched_chunks",
        "backups",
    ]
    
    for directory in essential_dirs:
        os.makedirs(directory, exist_ok=True)
        # Add .gitkeep to preserve empty directories
        gitkeep_path = os.path.join(directory, ".gitkeep")
        if not os.path.exists(gitkeep_path):
            with open(gitkeep_path, 'w') as f:
                f.write("# This file ensures the directory is preserved in git\n")
    
    logger.info(f"✅ Created {len(essential_dirs)} essential directories")

def create_production_config():
    """Create production configuration template."""
    logger.info("⚙️  Creating production configuration...")
    
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Create production config template
    production_config = {
        "version": "1.0.0-beta",
        "environment": "production",
        "model": {
            "provider": "ollama",
            "model_name": "hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M",
            "api_url": "http://localhost:11434"
        },
        "memory": {
            "backend": "simple",
            "max_memories": 10000,
            "embedding_model": "all-MiniLM-L6-v2",
            "storage_dir": "memory_store"
        },
        "ui": {
            "chat_port": 5001,
            "memory_ui_port": 8501,
            "host": "0.0.0.0",
            "auto_open_browser": True
        },
        "features": {
            "show_thoughts": True,
            "thoughts_default_hidden": True,
            "enable_thought_toggle": True,
            "web_search": False,
            "document_upload": True,
            "memory_management": True
        },
        "security": {
            "enable_auth": False,
            "auth_secret_key": "",
            "allowed_origins": ["*"]
        },
        "logging": {
            "level": "INFO",
            "file": "logs/sam.log",
            "max_size": "10MB",
            "backup_count": 5
        }
    }
    
    config_file = config_dir / "sam_config.json"
    with open(config_file, 'w') as f:
        json.dump(production_config, f, indent=2)
    
    logger.info(f"✅ Created production config: {config_file}")

def main():
    """Main preparation function."""
    logger.info("🚀 Starting SAM Beta Release Preparation")
    logger.info("=" * 60)
    
    try:
        # Step 1: Clean up development files
        removed_count = cleanup_development_files()
        
        # Step 2: Create production directories
        create_production_directories()
        
        # Step 3: Create production configuration
        create_production_config()
        
        logger.info("=" * 60)
        logger.info("🎉 SAM Beta Release Preparation Complete!")
        logger.info(f"📊 Summary:")
        logger.info(f"   - Removed {removed_count} development files")
        logger.info(f"   - Created production directory structure")
        logger.info(f"   - Generated production configuration")
        logger.info("")
        logger.info("📋 Next steps:")
        logger.info("1. Review config/sam_config.json")
        logger.info("2. Test installation with: python install.py")
        logger.info("3. Test startup with: python start_sam.py")
        logger.info("4. Package for distribution")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during preparation: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
