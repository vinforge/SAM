#!/usr/bin/env python3
"""
SAM Phase 2: Data Migration Script
Migrates existing JSON memory files to ChromaDB with enhanced Citation schema.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from memory.memory_vectorstore import MemoryVectorStore, VectorStoreType, MemoryType, MemoryChunk
from utils.chroma_client import get_chroma_client, get_chroma_collection, load_chroma_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChromaMigrator:
    """Handles migration from JSON files to ChromaDB."""
    
    def __init__(self, source_dir: str = "web_ui/memory_store", 
                 target_dir: str = "web_ui/chroma_db",
                 backup_dir: str = "web_ui/memory_store_backup"):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.backup_dir = Path(backup_dir)
        self.stats = {
            "total_files": 0,
            "migrated": 0,
            "skipped": 0,
            "errors": 0,
            "summary_chunks": 0,
            "content_blocks": 0
        }
        
    def analyze_existing_data(self) -> Dict[str, Any]:
        """Analyze existing JSON memory files."""
        logger.info("🔍 Analyzing existing memory data...")
        
        analysis = {
            "total_files": 0,
            "file_types": {},
            "memory_types": {},
            "source_patterns": {},
            "metadata_fields": set(),
            "sample_files": []
        }
        
        if not self.source_dir.exists():
            logger.warning(f"Source directory not found: {self.source_dir}")
            return analysis
            
        json_files = list(self.source_dir.glob("mem_*.json"))
        analysis["total_files"] = len(json_files)
        
        for i, file_path in enumerate(json_files[:10]):  # Sample first 10 files
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Analyze memory type
                memory_type = data.get("memory_type", "unknown")
                analysis["memory_types"][memory_type] = analysis["memory_types"].get(memory_type, 0) + 1
                
                # Analyze source patterns
                source = data.get("source", "")
                if ":" in source:
                    source_type = source.split(":")[0]
                    analysis["source_patterns"][source_type] = analysis["source_patterns"].get(source_type, 0) + 1
                
                # Collect metadata fields
                metadata = data.get("metadata", {})
                analysis["metadata_fields"].update(metadata.keys())
                
                # Determine file type
                if "summary" in data.get("tags", []) or metadata.get("document_type") == "summary":
                    file_type = "summary"
                elif "content_block" in data.get("tags", []) or metadata.get("document_type") == "content_block":
                    file_type = "content_block"
                else:
                    file_type = "other"
                    
                analysis["file_types"][file_type] = analysis["file_types"].get(file_type, 0) + 1
                
                # Store sample for inspection
                if i < 3:
                    analysis["sample_files"].append({
                        "file": file_path.name,
                        "memory_type": memory_type,
                        "source": source,
                        "content_length": len(data.get("content", "")),
                        "metadata_keys": list(metadata.keys())
                    })
                    
            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")
                
        logger.info(f"📊 Analysis complete: {analysis['total_files']} files found")
        logger.info(f"   Memory types: {dict(analysis['memory_types'])}")
        logger.info(f"   File types: {dict(analysis['file_types'])}")
        logger.info(f"   Source patterns: {dict(analysis['source_patterns'])}")
        logger.info(f"   Metadata fields: {len(analysis['metadata_fields'])} unique fields")
        
        return analysis
    
    def create_backup(self) -> bool:
        """Create backup of existing memory files."""
        try:
            if self.backup_dir.exists():
                logger.warning(f"Backup directory already exists: {self.backup_dir}")
                return True
                
            logger.info(f"📦 Creating backup: {self.source_dir} -> {self.backup_dir}")
            
            import shutil
            shutil.copytree(self.source_dir, self.backup_dir)
            
            logger.info(f"✅ Backup created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return False
    
    def load_memory_chunk_from_json(self, file_path: Path) -> Optional[MemoryChunk]:
        """Load a MemoryChunk from JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Convert memory type
            memory_type_str = data.get("memory_type", "document")
            if memory_type_str == "document":
                memory_type = MemoryType.DOCUMENT
            elif memory_type_str == "conversation":
                memory_type = MemoryType.CONVERSATION
            elif memory_type_str == "system":
                memory_type = MemoryType.SYSTEM
            else:
                memory_type = MemoryType.DOCUMENT
            
            # Create MemoryChunk
            chunk = MemoryChunk(
                chunk_id=data.get("chunk_id"),
                content=data.get("content", ""),
                content_hash=data.get("content_hash", ""),
                embedding=data.get("embedding", []),
                memory_type=memory_type,
                source=data.get("source", ""),
                timestamp=data.get("timestamp", ""),
                tags=data.get("tags", []),
                importance_score=data.get("importance_score", 0.0),
                access_count=data.get("access_count", 0),
                last_accessed=data.get("last_accessed", ""),
                metadata=data.get("metadata", {})
            )
            
            return chunk
            
        except Exception as e:
            logger.error(f"Error loading memory chunk from {file_path}: {e}")
            return None
    
    def migrate_to_chroma(self, dry_run: bool = False) -> bool:
        """Migrate all JSON files to ChromaDB."""
        logger.info(f"🚀 Starting migration to ChromaDB (dry_run={dry_run})")
        
        # Initialize ChromaDB vector store
        try:
            if not dry_run:
                chroma_store = MemoryVectorStore(
                    store_type=VectorStoreType.CHROMA,
                    storage_directory=str(self.target_dir.parent),
                    embedding_dimension=384
                )
                logger.info("✅ ChromaDB vector store initialized")
            else:
                logger.info("🔍 Dry run mode - no actual migration")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize ChromaDB: {e}")
            return False
        
        # Process all JSON files
        json_files = list(self.source_dir.glob("mem_*.json"))
        self.stats["total_files"] = len(json_files)
        
        logger.info(f"📁 Found {len(json_files)} memory files to migrate")
        
        for i, file_path in enumerate(json_files):
            try:
                # Load memory chunk
                chunk = self.load_memory_chunk_from_json(file_path)
                if not chunk:
                    self.stats["errors"] += 1
                    continue
                
                # Categorize chunk type
                if "summary" in chunk.tags or chunk.metadata.get("document_type") == "summary":
                    self.stats["summary_chunks"] += 1
                elif "content_block" in chunk.tags or chunk.metadata.get("document_type") == "content_block":
                    self.stats["content_blocks"] += 1
                
                if not dry_run:
                    # Add to ChromaDB
                    chroma_store.memory_chunks[chunk.chunk_id] = chunk
                    chroma_store._add_to_vector_index(chunk.chunk_id, chunk.embedding)
                    
                self.stats["migrated"] += 1
                
                # Progress logging
                if (i + 1) % 10 == 0:
                    logger.info(f"   Processed {i + 1}/{len(json_files)} files...")
                    
            except Exception as e:
                logger.error(f"Error migrating {file_path}: {e}")
                self.stats["errors"] += 1
        
        logger.info("✅ Migration completed!")
        self.print_migration_stats()
        return True
    
    def print_migration_stats(self):
        """Print migration statistics."""
        logger.info("📊 Migration Statistics:")
        logger.info(f"   Total files: {self.stats['total_files']}")
        logger.info(f"   Successfully migrated: {self.stats['migrated']}")
        logger.info(f"   Errors: {self.stats['errors']}")
        logger.info(f"   Summary chunks: {self.stats['summary_chunks']}")
        logger.info(f"   Content blocks: {self.stats['content_blocks']}")
        
        if self.stats["total_files"] > 0:
            success_rate = (self.stats["migrated"] / self.stats["total_files"]) * 100
            logger.info(f"   Success rate: {success_rate:.1f}%")

def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(description="Migrate SAM memory data to ChromaDB")
    parser.add_argument("--analyze", action="store_true", help="Analyze existing data only")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without actual migration")
    parser.add_argument("--backup", action="store_true", help="Create backup before migration")
    parser.add_argument("--source", default="web_ui/memory_store", help="Source directory")
    parser.add_argument("--target", default="web_ui/chroma_db", help="Target directory")
    
    args = parser.parse_args()
    
    migrator = ChromaMigrator(
        source_dir=args.source,
        target_dir=args.target
    )
    
    print("🔄 SAM Phase 2: Data Migration to ChromaDB")
    print("=" * 50)
    
    # Step 1: Analyze existing data
    analysis = migrator.analyze_existing_data()
    
    if args.analyze:
        print("\n📋 Analysis complete. Use --dry-run to test migration.")
        return
    
    # Step 2: Create backup if requested
    if args.backup:
        if not migrator.create_backup():
            print("❌ Backup failed. Aborting migration.")
            return
    
    # Step 3: Migrate data
    success = migrator.migrate_to_chroma(dry_run=args.dry_run)
    
    if success:
        if args.dry_run:
            print("\n✅ Dry run completed successfully!")
            print("Run without --dry-run to perform actual migration.")
        else:
            print("\n🎉 Migration completed successfully!")
            print("ChromaDB is now ready with enhanced Citation schema.")
    else:
        print("\n❌ Migration failed. Check logs for details.")

if __name__ == "__main__":
    main()
