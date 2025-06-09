"""
SAM Bulk Ingestion UI - Phase 2
Streamlit interface for managing bulk document ingestion sources and operations.
"""

import streamlit as st
import json
import subprocess
import threading
import time
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

class BulkIngestionManager:
    """Manages bulk ingestion sources and operations."""
    
    def __init__(self):
        self.config_file = Path("data/bulk_ingestion_config.json")
        self.state_db = Path("data/ingestion_state.db")
        self.log_file = Path("logs/bulk_ingest.log")
        
        # Ensure directories exist
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize configuration
        self._init_config()
    
    def _init_config(self):
        """Initialize configuration file if it doesn't exist."""
        if not self.config_file.exists():
            default_config = {
                "version": "1.0",
                "sources": [],
                "settings": {
                    "auto_scan_enabled": False,
                    "scan_interval_minutes": 60,
                    "default_file_types": ["pdf", "txt", "md", "docx", "py", "js", "json"],
                    "max_file_size_mb": 100,
                    "enable_notifications": True
                },
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading configuration: {e}")
            return {"sources": [], "settings": {}}
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        try:
            config["last_updated"] = datetime.now().isoformat()
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            st.error(f"Error saving configuration: {e}")
    
    def add_source(self, path: str, name: str, file_types: List[str], enabled: bool = True) -> bool:
        """Add a new ingestion source."""
        try:
            config = self.load_config()
            
            # Check if source already exists
            for source in config["sources"]:
                if source["path"] == path:
                    return False
            
            new_source = {
                "id": f"source_{len(config['sources']) + 1}",
                "name": name,
                "path": path,
                "file_types": file_types,
                "enabled": enabled,
                "added_date": datetime.now().isoformat(),
                "last_scanned": None,
                "status": "ready",
                "files_processed": 0,
                "last_scan_results": {}
            }
            
            config["sources"].append(new_source)
            self.save_config(config)
            return True
            
        except Exception as e:
            st.error(f"Error adding source: {e}")
            return False
    
    def remove_source(self, source_id: str) -> bool:
        """Remove an ingestion source."""
        try:
            config = self.load_config()
            config["sources"] = [s for s in config["sources"] if s["id"] != source_id]
            self.save_config(config)
            return True
        except Exception as e:
            st.error(f"Error removing source: {e}")
            return False
    
    def update_source(self, source_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing source."""
        try:
            config = self.load_config()
            for source in config["sources"]:
                if source["id"] == source_id:
                    source.update(updates)
                    break
            self.save_config(config)
            return True
        except Exception as e:
            st.error(f"Error updating source: {e}")
            return False
    
    def get_ingestion_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics from the state database."""
        try:
            if not self.state_db.exists():
                return {
                    'total_files': 0,
                    'total_chunks': 0,
                    'avg_enrichment': 0.0,
                    'successful': 0,
                    'failed': 0,
                    'recent_activity': []
                }
            
            with sqlite3.connect(self.state_db) as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_files,
                        SUM(chunks_created) as total_chunks,
                        AVG(enrichment_score) as avg_enrichment,
                        COUNT(CASE WHEN status = 'success' THEN 1 END) as successful,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed
                    FROM processed_files
                """)
                result = cursor.fetchone()
                
                # Get recent activity
                recent_cursor = conn.execute("""
                    SELECT filepath, processed_at, status, enrichment_score, chunks_created
                    FROM processed_files 
                    ORDER BY processed_at DESC 
                    LIMIT 10
                """)
                recent_activity = recent_cursor.fetchall()
                
                return {
                    'total_files': result[0] or 0,
                    'total_chunks': result[1] or 0,
                    'avg_enrichment': result[2] or 0.0,
                    'successful': result[3] or 0,
                    'failed': result[4] or 0,
                    'recent_activity': [
                        {
                            'filepath': row[0],
                            'processed_at': row[1],
                            'status': row[2],
                            'enrichment_score': row[3],
                            'chunks_created': row[4]
                        }
                        for row in recent_activity
                    ]
                }
        except Exception as e:
            st.error(f"Error getting stats: {e}")
            return {}
    
    def run_bulk_ingestion(self, source_path: str, file_types: List[str], dry_run: bool = False) -> Dict[str, Any]:
        """Run bulk ingestion for a specific source."""
        try:
            # Build command
            cmd = [
                sys.executable, "scripts/bulk_ingest.py",
                "--source", source_path
            ]
            
            if file_types:
                cmd.extend(["--file-types", ",".join(file_types)])
            
            if dry_run:
                cmd.append("--dry-run")
            
            cmd.append("--verbose")
            
            # Run command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1
            }

class BulkIngestionUI:
    """Streamlit UI for bulk ingestion management."""
    
    def __init__(self):
        self.manager = BulkIngestionManager()
    
    def render(self):
        """Render the bulk ingestion UI."""
        st.subheader("📁 Bulk Document Ingestion")
        st.markdown("Manage document sources and bulk ingestion operations")
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs([
            "📂 Source Management",
            "🚀 Manual Scan",
            "📊 Statistics",
            "⚙️ Settings"
        ])
        
        with tab1:
            self._render_source_management()
        
        with tab2:
            self._render_manual_scan()
        
        with tab3:
            self._render_statistics()
        
        with tab4:
            self._render_settings()
    
    def _render_source_management(self):
        """Render the source management interface."""
        st.markdown("### 📂 Manage Knowledge Sources")
        st.markdown("Add and manage folders that SAM monitors for documents")

        # Information panel
        with st.expander("ℹ️ How Document Processing Works", expanded=False):
            st.markdown("""
            **What happens when you add and process sources:**

            1. **📁 Add Source:** Configure a folder path and file types to monitor
            2. **🚀 Process Files:** Scan the folder and process supported documents
            3. **🧠 Data Enrichment:** Extract content, generate embeddings, and create metadata
            4. **💾 Memory Storage:** Store processed content in SAM's knowledge base
            5. **🔍 Knowledge Consolidation:** Optimize and organize memories for better retrieval
            6. **💬 Ready for Q&A:** Ask SAM questions about the processed documents

            **Processing Options:**
            - **🔍 Preview (Dry Run):** See what files will be processed without actually processing them
            - **🚀 Process:** Actually process files and add them to SAM's knowledge base
            - **🧠 Auto-Consolidate:** Automatically run knowledge consolidation after processing

            **Note:** Adding a source only configures it - you must trigger processing to add files to SAM's knowledge base.
            """)

        st.divider()
        
        config = self.manager.load_config()
        sources = config.get("sources", [])
        
        # Add new source section
        with st.expander("➕ Add New Source", expanded=len(sources) == 0):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Enhanced path input with platform-specific examples
                import platform
                system = platform.system()

                if system == "Windows":
                    placeholder = "C:\\Users\\username\\Documents"
                    help_text = "Enter the full Windows path (e.g., C:\\Users\\username\\Documents)"
                elif system == "Darwin":  # macOS
                    placeholder = "/Users/username/Documents"
                    help_text = "Enter the full macOS path (e.g., /Users/username/Documents or ~/Documents)"
                else:  # Linux and others
                    placeholder = "/home/username/documents"
                    help_text = "Enter the full Linux path (e.g., /home/username/documents or ~/documents)"

                source_path = st.text_input(
                    "Folder Path",
                    placeholder=placeholder,
                    help=help_text
                )

                # Add common path suggestions
                if st.button("📁 Common Paths", help="Show common document folder paths"):
                    st.session_state.show_common_paths = not st.session_state.get("show_common_paths", False)

                if st.session_state.get("show_common_paths", False):
                    st.markdown("**Common Document Paths:**")
                    if system == "Windows":
                        common_paths = [
                            "C:\\Users\\%USERNAME%\\Documents",
                            "C:\\Users\\%USERNAME%\\Desktop",
                            "C:\\Users\\%USERNAME%\\Downloads"
                        ]
                    elif system == "Darwin":  # macOS
                        common_paths = [
                            "~/Documents",
                            "~/Desktop",
                            "~/Downloads",
                            "/Users/$USER/Documents"
                        ]
                    else:  # Linux
                        common_paths = [
                            "~/Documents",
                            "~/Desktop",
                            "~/Downloads",
                            "/home/$USER/documents"
                        ]

                    for path in common_paths:
                        if st.button(f"📂 {path}", key=f"path_{path}"):
                            st.session_state.selected_path = path
                            st.rerun()

                # Use selected path if available
                if st.session_state.get("selected_path"):
                    source_path = st.session_state.selected_path
                    st.session_state.selected_path = None  # Clear after use

                source_name = st.text_input(
                    "Source Name",
                    placeholder="Research Papers",
                    help="A friendly name for this source"
                )
            
            with col2:
                default_types = config.get("settings", {}).get("default_file_types", ["pdf", "txt", "md"])
                file_types = st.multiselect(
                    "File Types",
                    options=["pdf", "txt", "md", "docx", "doc", "py", "js", "html", "json", "csv"],
                    default=default_types,
                    help="Select which file types to process"
                )
                
                enabled = st.checkbox("Enable Source", value=True)
            
            # Processing options
            col1, col2 = st.columns(2)
            with col1:
                auto_scan = st.checkbox(
                    "🚀 Scan immediately after adding",
                    value=True,
                    help="Automatically scan the source after adding it"
                )
            with col2:
                dry_run_new = st.checkbox(
                    "🔍 Dry run first",
                    value=False,
                    help="Preview what will be processed before actual scanning"
                )

            if st.button("➕ Add Source", type="primary"):
                if source_path and source_name:
                    # Enhanced cross-platform path validation
                    path_validation = self._validate_path(source_path)

                    if path_validation["valid"]:
                        # Use the normalized path
                        normalized_path = path_validation["normalized_path"]

                        if self.manager.add_source(normalized_path, source_name, file_types, enabled):
                            st.success(f"✅ Added source: {source_name}")
                            st.info(f"📁 Normalized path: `{normalized_path}`")

                            # Auto-scan if requested
                            if auto_scan and enabled:
                                st.info(f"🚀 {'Previewing' if dry_run_new else 'Processing'} files in {source_name}...")

                                with st.spinner(f"{'Scanning' if dry_run_new else 'Processing'} {source_name}..."):
                                    result = self.manager.run_bulk_ingestion(
                                        normalized_path,
                                        file_types,
                                        dry_run=dry_run_new
                                    )

                                # Display immediate results
                                if result["success"]:
                                    st.success(f"✅ {source_name}: {'Preview' if dry_run_new else 'Processing'} completed!")

                                    # Show summary
                                    stdout = result["stdout"]
                                    if "Bulk Ingestion Summary:" in stdout:
                                        summary_start = stdout.find("Bulk Ingestion Summary:")
                                        summary_section = stdout[summary_start:summary_start+300]
                                        st.code(summary_section)

                                        if dry_run_new:
                                            st.info("🔍 This was a preview. Go to 'Manual Scan' tab to process files.")
                                        else:
                                            st.success("🎉 Files have been processed and added to SAM's knowledge base!")
                                else:
                                    st.error(f"❌ {source_name}: {'Preview' if dry_run_new else 'Processing'} failed")
                                    if result["stderr"]:
                                        st.error(result["stderr"])

                            st.rerun()
                        else:
                            st.error("❌ Source already exists or failed to add")
                    else:
                        # Show detailed path validation error
                        st.error(f"❌ Path validation failed: {path_validation['error']}")

                        # Show debugging information
                        with st.expander("🔍 Path Debugging Information"):
                            st.code(f"""
Original path: {source_path}
Normalized path: {path_validation.get('normalized_path', 'N/A')}
Path exists: {path_validation.get('exists', False)}
Is directory: {path_validation.get('is_directory', False)}
Platform: {path_validation.get('platform', 'Unknown')}
Error details: {path_validation.get('error_details', 'None')}
                            """)
                else:
                    st.error("❌ Please fill in all required fields")
        
        # Display existing sources
        if sources:
            # Quick actions for all sources
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🚀 Process All Enabled Sources", type="secondary"):
                    enabled_sources = [s for s in sources if s["enabled"]]
                    if enabled_sources:
                        st.session_state.trigger_bulk_scan = True
                        st.rerun()
                    else:
                        st.warning("⚠️ No enabled sources to process")

            with col2:
                if st.button("🔍 Preview All Sources", type="secondary"):
                    enabled_sources = [s for s in sources if s["enabled"]]
                    if enabled_sources:
                        st.session_state.trigger_bulk_preview = True
                        st.rerun()
                    else:
                        st.warning("⚠️ No enabled sources to preview")

            with col3:
                if st.button("📊 View Processing Stats", type="secondary"):
                    st.session_state.show_stats_popup = True

            # Handle bulk operations
            if st.session_state.get("trigger_bulk_scan", False):
                st.session_state.trigger_bulk_scan = False
                self._run_bulk_operation([s for s in sources if s["enabled"]], dry_run=False)

            if st.session_state.get("trigger_bulk_preview", False):
                st.session_state.trigger_bulk_preview = False
                self._run_bulk_operation([s for s in sources if s["enabled"]], dry_run=True)

            st.markdown("### 📋 Current Sources")

            for i, source in enumerate(sources):
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    
                    with col1:
                        status_icon = "🟢" if source["enabled"] else "🔴"
                        st.markdown(f"**{status_icon} {source['name']}**")
                        st.caption(f"📁 {source['path']}")
                        
                        # Show file types
                        types_str = ", ".join(source["file_types"])
                        st.caption(f"📄 Types: {types_str}")
                    
                    with col2:
                        st.caption(f"**Status:** {source['status'].title()}")
                        if source.get("last_scanned"):
                            last_scan = source["last_scanned"][:10]
                            st.caption(f"**Last Scan:** {last_scan}")
                        else:
                            st.caption("**Last Scan:** Never")
                        
                        files_processed = source.get("files_processed", 0)
                        st.caption(f"**Files Processed:** {files_processed}")
                    
                    with col3:
                        # Toggle enabled/disabled
                        new_enabled = st.checkbox(
                            "Enabled",
                            value=source["enabled"],
                            key=f"enabled_{source['id']}"
                        )
                        
                        if new_enabled != source["enabled"]:
                            self.manager.update_source(source["id"], {"enabled": new_enabled})
                            st.rerun()
                    
                    with col4:
                        # Action buttons
                        if st.button("🗑️", key=f"delete_{source['id']}", help="Delete source"):
                            if self.manager.remove_source(source["id"]):
                                st.success("✅ Source removed")
                                st.rerun()
                        
                        if st.button("🔍", key=f"scan_{source['id']}", help="Scan this source"):
                            st.session_state[f"scan_source_{source['id']}"] = True
                            st.rerun()
                    
                    st.divider()
        else:
            st.info("📝 No sources configured. Add a source above to get started.")

    def _validate_path(self, path_str: str) -> Dict[str, Any]:
        """Enhanced cross-platform path validation."""
        import os
        import platform

        try:
            # Clean and normalize the path
            cleaned_path = path_str.strip()

            # Handle different path formats
            if platform.system() == "Windows":
                # Handle Windows paths
                if cleaned_path.startswith("/") and not cleaned_path.startswith("//"):
                    # Convert Unix-style path to Windows if needed
                    cleaned_path = cleaned_path.replace("/", "\\")

                # Expand environment variables
                cleaned_path = os.path.expandvars(cleaned_path)

            else:
                # Handle Unix-like systems (macOS, Linux)
                # Expand user home directory (~)
                cleaned_path = os.path.expanduser(cleaned_path)

                # Expand environment variables
                cleaned_path = os.path.expandvars(cleaned_path)

            # Create Path object and resolve
            path_obj = Path(cleaned_path).resolve()

            # Check if path exists
            exists = path_obj.exists()
            is_directory = path_obj.is_dir() if exists else False

            # Additional checks for common issues
            error_details = []

            if not exists:
                # Check parent directory
                parent = path_obj.parent
                if parent.exists():
                    error_details.append(f"Parent directory exists: {parent}")
                    error_details.append("Path might be a typo or the directory needs to be created")
                else:
                    error_details.append(f"Parent directory does not exist: {parent}")

                # Check for case sensitivity issues (common on macOS)
                if platform.system() == "Darwin":  # macOS
                    try:
                        # Try to find similar paths with different case
                        parent_contents = list(parent.iterdir()) if parent.exists() else []
                        similar_names = [
                            p.name for p in parent_contents
                            if p.name.lower() == path_obj.name.lower()
                        ]
                        if similar_names:
                            error_details.append(f"Similar names found (case mismatch): {similar_names}")
                    except:
                        pass

            elif exists and not is_directory:
                error_details.append("Path exists but is not a directory")

            # Check permissions
            if exists and is_directory:
                try:
                    # Test read permission
                    list(path_obj.iterdir())
                    readable = True
                except PermissionError:
                    readable = False
                    error_details.append("Directory exists but is not readable (permission denied)")
                except:
                    readable = False
                    error_details.append("Directory exists but cannot be accessed")
            else:
                readable = False

            # Determine if path is valid
            valid = exists and is_directory and readable

            if valid:
                return {
                    "valid": True,
                    "normalized_path": str(path_obj),
                    "exists": exists,
                    "is_directory": is_directory,
                    "readable": readable,
                    "platform": platform.system(),
                    "original_path": path_str
                }
            else:
                error_msg = "Path validation failed"
                if not exists:
                    error_msg = "Path does not exist"
                elif not is_directory:
                    error_msg = "Path is not a directory"
                elif not readable:
                    error_msg = "Directory is not readable"

                return {
                    "valid": False,
                    "error": error_msg,
                    "normalized_path": str(path_obj),
                    "exists": exists,
                    "is_directory": is_directory,
                    "readable": readable,
                    "platform": platform.system(),
                    "original_path": path_str,
                    "error_details": error_details
                }

        except Exception as e:
            return {
                "valid": False,
                "error": f"Path validation error: {str(e)}",
                "normalized_path": cleaned_path if 'cleaned_path' in locals() else path_str,
                "exists": False,
                "is_directory": False,
                "readable": False,
                "platform": platform.system(),
                "original_path": path_str,
                "error_details": [f"Exception: {str(e)}"]
            }

    def _run_bulk_operation(self, sources: List[Dict], dry_run: bool):
        """Run bulk operation on multiple sources from source management."""
        if not sources:
            st.warning("⚠️ No enabled sources to process")
            return

        operation_type = "Preview" if dry_run else "Processing"
        st.info(f"🚀 {operation_type} {len(sources)} source(s)...")

        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()

        total_sources = len(sources)
        successful = 0
        failed = 0

        for i, source in enumerate(sources):
            progress = (i + 1) / total_sources
            progress_bar.progress(progress)
            status_text.text(f"{operation_type} {source['name']} ({i+1}/{total_sources})")

            result = self.manager.run_bulk_ingestion(
                source["path"],
                source["file_types"],
                dry_run
            )

            if result["success"]:
                successful += 1
            else:
                failed += 1

            with results_container:
                self._display_scan_result(source["name"], result, dry_run)

        # Final summary
        status_text.text(f"✅ {operation_type} completed: {successful} successful, {failed} failed")
        progress_bar.progress(1.0)

        if not dry_run and successful > 0:
            st.success(f"🎉 {successful} source(s) processed successfully! Files have been added to SAM's knowledge base.")

            # Trigger knowledge consolidation
            if st.button("🧠 Consolidate Knowledge", type="primary", help="Run knowledge consolidation to optimize SAM's memory"):
                self._trigger_knowledge_consolidation()

    def _trigger_knowledge_consolidation(self):
        """Trigger knowledge consolidation after successful processing."""
        try:
            with st.spinner("🧠 Running knowledge consolidation..."):
                # Import and run knowledge consolidation
                from memory.knowledge_consolidation import run_knowledge_consolidation

                result = run_knowledge_consolidation()

                if result.get("success", False):
                    st.success("✅ Knowledge consolidation completed successfully!")
                    st.info(f"📊 Consolidated {result.get('memories_processed', 0)} memories")

                    # Show consolidation metrics
                    if result.get("metrics"):
                        metrics = result["metrics"]
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("Memories Processed", metrics.get("total_memories", 0))
                        with col2:
                            st.metric("Summaries Created", metrics.get("summaries_created", 0))
                        with col3:
                            st.metric("Quality Score", f"{metrics.get('avg_quality', 0):.2f}")
                else:
                    st.warning("⚠️ Knowledge consolidation completed with warnings")
                    if result.get("message"):
                        st.info(result["message"])

        except ImportError:
            st.warning("⚠️ Knowledge consolidation not available - feature may not be implemented yet")
        except Exception as e:
            st.error(f"❌ Knowledge consolidation failed: {e}")

    def _render_manual_scan(self):
        """Render the manual scan interface."""
        st.markdown("### 🚀 Manual Scan Operations")
        st.markdown("Trigger bulk ingestion scans manually")
        
        config = self.manager.load_config()
        sources = config.get("sources", [])
        enabled_sources = [s for s in sources if s["enabled"]]
        
        if not enabled_sources:
            st.warning("⚠️ No enabled sources found. Please add and enable sources first.")
            return
        
        # Scan all sources
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 🔄 Scan All Sources")
            st.markdown("Process all enabled sources in sequence")
            
            dry_run_all = st.checkbox("Dry Run (Preview Only)", key="dry_run_all")
            
            if st.button("🚀 Scan All Sources", type="primary"):
                self._run_scan_all(enabled_sources, dry_run_all)
        
        with col2:
            st.markdown("#### ⚡ Quick Actions")
            
            if st.button("📊 View Statistics"):
                st.session_state.show_stats = True
            
            if st.button("📋 View Logs"):
                self._show_logs()
        
        # Individual source scanning
        st.markdown("#### 📂 Scan Individual Sources")
        
        for source in enabled_sources:
            with st.expander(f"🔍 {source['name']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Path:** `{source['path']}`")
                    st.markdown(f"**File Types:** {', '.join(source['file_types'])}")
                    
                    dry_run = st.checkbox(
                        "Dry Run (Preview Only)",
                        key=f"dry_run_{source['id']}"
                    )
                
                with col2:
                    if st.button(
                        "🚀 Scan Source",
                        key=f"scan_btn_{source['id']}",
                        type="secondary"
                    ):
                        self._run_individual_scan(source, dry_run)
        
        # Check for scan triggers from source management
        for source in sources:
            if st.session_state.get(f"scan_source_{source['id']}", False):
                st.session_state[f"scan_source_{source['id']}"] = False
                self._run_individual_scan(source, dry_run=True)
    
    def _run_scan_all(self, sources: List[Dict], dry_run: bool):
        """Run scan for all sources."""
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()
        
        total_sources = len(sources)
        
        for i, source in enumerate(sources):
            progress = (i + 1) / total_sources
            progress_bar.progress(progress)
            status_text.text(f"Scanning {source['name']} ({i+1}/{total_sources})")
            
            result = self.manager.run_bulk_ingestion(
                source["path"],
                source["file_types"],
                dry_run
            )
            
            with results_container:
                self._display_scan_result(source["name"], result, dry_run)
        
        status_text.text("✅ All scans completed!")
        progress_bar.progress(1.0)
    
    def _run_individual_scan(self, source: Dict, dry_run: bool):
        """Run scan for an individual source."""
        with st.spinner(f"Scanning {source['name']}..."):
            result = self.manager.run_bulk_ingestion(
                source["path"],
                source["file_types"],
                dry_run
            )
            
            self._display_scan_result(source["name"], result, dry_run)
    
    def _display_scan_result(self, source_name: str, result: Dict, dry_run: bool):
        """Display the result of a scan operation."""
        if result["success"]:
            st.success(f"✅ {source_name}: Scan completed successfully")
            
            # Parse output for summary
            stdout = result["stdout"]
            if "Bulk Ingestion Summary:" in stdout:
                summary_start = stdout.find("Bulk Ingestion Summary:")
                summary_section = stdout[summary_start:summary_start+500]
                
                with st.expander(f"📊 {source_name} Results"):
                    st.code(summary_section)
                    
                    if dry_run:
                        st.info("🔍 This was a dry run - no files were actually processed")
            
        else:
            st.error(f"❌ {source_name}: Scan failed")
            
            with st.expander(f"🔍 {source_name} Error Details"):
                if result["stderr"]:
                    st.code(result["stderr"])
                if result["stdout"]:
                    st.code(result["stdout"])
    
    def _render_statistics(self):
        """Render the statistics interface."""
        st.markdown("### 📊 Ingestion Statistics")
        
        stats = self.manager.get_ingestion_stats()
        
        if stats:
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Files", stats['total_files'])
            
            with col2:
                st.metric("Memory Chunks", stats['total_chunks'])
            
            with col3:
                st.metric("Success Rate", f"{stats['successful']}/{stats['total_files']}")
            
            with col4:
                avg_score = stats['avg_enrichment']
                st.metric("Avg Enrichment", f"{avg_score:.2f}")
            
            # Recent activity
            if stats['recent_activity']:
                st.markdown("#### 📋 Recent Activity")
                
                for activity in stats['recent_activity']:
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    
                    with col1:
                        filename = Path(activity['filepath']).name
                        st.markdown(f"**{filename}**")
                        st.caption(activity['filepath'])
                    
                    with col2:
                        processed_date = activity['processed_at'][:10]
                        st.caption(f"📅 {processed_date}")
                    
                    with col3:
                        status_icon = "✅" if activity['status'] == 'success' else "❌"
                        st.markdown(f"{status_icon} {activity['status']}")
                    
                    with col4:
                        score = activity['enrichment_score']
                        chunks = activity['chunks_created']
                        st.caption(f"Score: {score:.2f}")
                        st.caption(f"Chunks: {chunks}")
        else:
            st.info("📝 No ingestion statistics available yet. Run some scans to see data here.")
    
    def _render_settings(self):
        """Render the settings interface."""
        st.markdown("### ⚙️ Bulk Ingestion Settings")
        
        config = self.manager.load_config()
        settings = config.get("settings", {})
        
        # File type defaults
        st.markdown("#### 📄 Default File Types")
        default_types = st.multiselect(
            "Default file types for new sources",
            options=["pdf", "txt", "md", "docx", "doc", "py", "js", "html", "json", "csv", "xml", "yaml"],
            default=settings.get("default_file_types", ["pdf", "txt", "md"]),
            help="These file types will be pre-selected when adding new sources"
        )
        
        # Processing limits
        st.markdown("#### 🔧 Processing Limits")
        col1, col2 = st.columns(2)
        
        with col1:
            max_file_size = st.number_input(
                "Max File Size (MB)",
                min_value=1,
                max_value=1000,
                value=settings.get("max_file_size_mb", 100),
                help="Maximum file size to process"
            )
        
        with col2:
            enable_notifications = st.checkbox(
                "Enable Notifications",
                value=settings.get("enable_notifications", True),
                help="Show notifications when scans complete"
            )
        
        # Save settings
        if st.button("💾 Save Settings", type="primary"):
            settings.update({
                "default_file_types": default_types,
                "max_file_size_mb": max_file_size,
                "enable_notifications": enable_notifications
            })
            
            config["settings"] = settings
            self.manager.save_config(config)
            st.success("✅ Settings saved successfully!")
    
    def _show_logs(self):
        """Display recent logs."""
        try:
            if self.manager.log_file.exists():
                with open(self.manager.log_file, 'r') as f:
                    logs = f.read()
                
                # Show last 50 lines
                log_lines = logs.split('\n')[-50:]
                recent_logs = '\n'.join(log_lines)
                
                st.code(recent_logs, language="text")
            else:
                st.info("📝 No log file found yet.")
        except Exception as e:
            st.error(f"Error reading logs: {e}")

def render_bulk_ingestion():
    """Main function to render the bulk ingestion UI."""
    ui = BulkIngestionUI()
    ui.render()
