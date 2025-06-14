#!/usr/bin/env python3
"""
Debug script to inspect ChromaDB contents
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import chromadb
    from chromadb.config import Settings
    
    print("🔍 Inspecting ChromaDB contents...")
    print("=" * 50)
    
    # Check main ChromaDB location
    chroma_path = project_root / "memory_store" / "chroma_db"
    print(f"📁 ChromaDB Path: {chroma_path}")
    print(f"📁 Path exists: {chroma_path.exists()}")
    
    if chroma_path.exists():
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(
            path=str(chroma_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # List all collections (newer ChromaDB API)
        try:
            collections = client.list_collections()
            print(f"📚 Total Collections: {len(collections)}")

            # Try to access known collection names
            known_collections = ["sam_memory_store", "default", "documents"]

            for collection_name in known_collections:
                try:
                    collection = client.get_collection(collection_name)
                    print(f"\n📖 Collection: {collection_name}")
                    print(f"   📊 Document Count: {collection.count()}")

                    # Get sample documents
                    if collection.count() > 0:
                        sample = collection.get(limit=3, include=["metadatas", "documents"])
                        print(f"   📄 Sample Documents:")

                        for j, (doc_id, doc, metadata) in enumerate(zip(
                            sample["ids"],
                            sample["documents"],
                            sample["metadatas"]
                        )):
                            print(f"      {j+1}. ID: {doc_id}")
                            print(f"         Content: {doc[:100]}..." if len(doc) > 100 else f"         Content: {doc}")
                            print(f"         Source: {metadata.get('source', 'N/A')}")
                            print(f"         Type: {metadata.get('memory_type', 'N/A')}")
                            print()
                    else:
                        print("   ❌ Collection is empty")

                except Exception as e:
                    print(f"   ❌ Collection '{collection_name}' not found or error: {e}")

        except Exception as e:
            print(f"❌ Error listing collections: {e}")

            # Fallback: try to access the main collection directly
            try:
                collection = client.get_collection("sam_memory_store")
                print(f"\n📖 Direct access to sam_memory_store:")
                print(f"   📊 Document Count: {collection.count()}")
            except Exception as e2:
                print(f"   ❌ Could not access sam_memory_store: {e2}")
    
    # Also check other potential locations
    other_locations = [
        project_root / "chroma_db",
        project_root / "streamlit_data" / "chroma_db",
        project_root / "web_ui" / "chroma_db"
    ]
    
    print("\n🔍 Checking other potential ChromaDB locations:")
    for location in other_locations:
        if location.exists():
            print(f"📁 Found: {location}")
            try:
                client = chromadb.PersistentClient(
                    path=str(location),
                    settings=Settings(anonymized_telemetry=False)
                )
                collections = client.list_collections()
                print(f"   📚 Collections: {len(collections)}")

                # Try known collection names
                for collection_name in ["sam_memory_store", "default", "documents"]:
                    try:
                        collection = client.get_collection(collection_name)
                        print(f"      - {collection_name}: {collection.count()} documents")
                    except:
                        pass
            except Exception as e:
                print(f"   ❌ Error reading: {e}")
        else:
            print(f"❌ Not found: {location}")

except ImportError as e:
    print(f"❌ ChromaDB not available: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
