#!/usr/bin/env python3
"""
SAM Community Edition - Release Cleanup Script
Prepares the SAM codebase for community release by removing unnecessary files.
"""

import os
import shutil
import glob
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cleanup_for_release():
    """Clean up the SAM codebase for community release."""
    
    logger.info("🧹 Starting SAM Community Edition cleanup...")
    
    # Files and directories to remove
    cleanup_targets = [
        # Development and testing files
        "__pycache__",
        "*.pyc",
        "*.pyo", 
        "*.pyd",
        ".pytest_cache",
        
        # Personal/development directories
        "MyStuff",
        "backups",
        "temp_uploads",
        
        # Development logs and databases
        "curiosity.log",
        "enrichment.log",
        "logs/curiosity_signals.db",
        "logs/retrieval_logs.db",
        "logs/sam_knowledge.db",
        "logs/sam_launcher.log",
        
        # Test files (keep test framework, remove specific test data)
        "test_*.py",
        "debug_*.py",
        "check_*.py",
        "process_*.py",
        
        # Development documentation
        "steps*.md",
        "SPRINT_*.md",
        "DIAGNOSTIC_*.md",
        "KNOWLEDGE_*.md",
        "LONGBIOBENCH_*.md",
        "MEMORY_*.md",
        "test_*.md",
        
        # Development data
        "execution_logs",
        "task_run_reports",
        
        # User data (will be recreated on first run)
        "memory_store/*.json",
        "multimodal_output",
        "data/uploads/*",
        "data/documents/*",
        "data/vector_store/*",
        "web_ui/uploads/*",
        "web_ui/data/*",
        "web_ui/memory_store/*",
        "web_ui/multimodal_output/*",
        
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
        
        # Development scripts
        "demo_*.py",
        "start_sprint*.py",
        "launch_*.py",  # Keep main launchers, remove dev ones
        "streamlit_*.py",
        "migrate_*.py",
        
        # Development prompts and configs
        "curious_analyst_prompt.txt",
        "sam_tool_augmented_prompt.txt",
        
        # Experimental directories
        "DE",  # Data Enrichment experimental
        "KC",  # Knowledge Consolidation experimental
        "deepseek_enhanced_learning",  # Experimental learning
        "knowledge_enrichment",
        "capsules",
        "watcher",
        
        # Docker files (will provide separate Docker setup)
        "Dockerfile",
        "docker-compose.yml",
        "sam.service",
        
        # Development utilities
        "enhanced_*.py",
        "gpu_*.py",
        "domain_*.py",
        "knowledge_navigator.py",
        "cli_tools.py",
        "main.py",  # Keep start_sam.py instead
    ]
    
    # Keep these essential files
    essential_files = [
        "README.md",
        "requirements.txt",
        "launch_web_ui.py",  # Main web UI launcher
        "start_sam.py",      # Main SAM launcher
        "SAM-whitepaper.md",
        "DEPLOYMENT.md",
        "Makefile",
    ]
    
    # Directories to keep but clean
    keep_but_clean = {
        "logs": ["*.log", "*.db"],
        "data": ["*"],
        "memory_store": ["*.json"],
        "multimodal_output": ["*"],
        "web_ui/uploads": ["*"],
        "web_ui/data": ["*"],
        "web_ui/memory_store": ["*"],
        "web_ui/multimodal_output": ["*"],
        "temp_uploads": ["*"],
        "vector_store": ["*"],
        "models": ["*"],  # Will be downloaded on first run
    }
    
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
    
    # Clean but keep directories
    for directory, patterns in keep_but_clean.items():
        if os.path.exists(directory):
            for pattern in patterns:
                matches = glob.glob(os.path.join(directory, pattern))
                for match in matches:
                    try:
                        if os.path.isfile(match):
                            os.remove(match)
                            logger.info(f"🧹 Cleaned file: {match}")
                            removed_count += 1
                    except Exception as e:
                        logger.warning(f"⚠️  Could not clean {match}: {e}")
            
            # Ensure directory exists but is empty
            os.makedirs(directory, exist_ok=True)
    
    # Create essential empty directories
    essential_dirs = [
        "logs",
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
    ]
    
    for directory in essential_dirs:
        os.makedirs(directory, exist_ok=True)
        # Add .gitkeep to preserve empty directories
        gitkeep_path = os.path.join(directory, ".gitkeep")
        if not os.path.exists(gitkeep_path):
            with open(gitkeep_path, 'w') as f:
                f.write("# This file ensures the directory is preserved in git\n")
    
    logger.info(f"✅ Cleanup complete! Removed {removed_count} files/directories")
    logger.info("🎯 SAM Community Edition is ready for release!")

if __name__ == "__main__":
    cleanup_for_release()
