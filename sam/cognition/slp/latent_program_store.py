"""
Latent Program Store
===================

Database layer for storing and retrieving latent programs with SQLite backend
and efficient querying capabilities.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from .latent_program import LatentProgram
from .program_signature import ProgramSignature

logger = logging.getLogger(__name__)


class LatentProgramStore:
    """
    SQLite-based storage system for latent programs.
    
    Provides efficient storage, retrieval, and querying of cognitive programs
    with support for similarity matching and performance analytics.
    """
    
    def __init__(self, db_path: str = "data/latent_programs.db"):
        """Initialize the program store."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize the database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS latent_programs (
                        id TEXT PRIMARY KEY,
                        signature_hash TEXT NOT NULL,
                        signature_data TEXT NOT NULL,
                        program_data TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        last_used TIMESTAMP NOT NULL,
                        usage_count INTEGER DEFAULT 0,
                        success_rate REAL DEFAULT 1.0,
                        confidence_score REAL DEFAULT 0.5,
                        user_feedback_score REAL DEFAULT 0.0,
                        is_active BOOLEAN DEFAULT 1,
                        is_experimental BOOLEAN DEFAULT 1,
                        version INTEGER DEFAULT 1,
                        parent_program_id TEXT,
                        avg_latency_ms REAL DEFAULT 0.0,
                        avg_token_count INTEGER DEFAULT 0
                    )
                """)
                
                # Create indexes for efficient querying
                conn.execute("CREATE INDEX IF NOT EXISTS idx_signature_hash ON latent_programs(signature_hash)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_active ON latent_programs(is_active)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_confidence ON latent_programs(confidence_score)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_last_used ON latent_programs(last_used)")
                
                # Create analytics table for performance tracking
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS program_executions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        program_id TEXT NOT NULL,
                        executed_at TIMESTAMP NOT NULL,
                        execution_time_ms REAL NOT NULL,
                        token_count INTEGER NOT NULL,
                        success BOOLEAN NOT NULL,
                        quality_score REAL,
                        user_feedback REAL,
                        FOREIGN KEY (program_id) REFERENCES latent_programs(id)
                    )
                """)
                
                conn.execute("CREATE INDEX IF NOT EXISTS idx_executions_program ON program_executions(program_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_executions_time ON program_executions(executed_at)")
                
                conn.commit()
                logger.info("Latent program database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def store_program(self, program: LatentProgram) -> bool:
        """Store a latent program in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Convert program to JSON
                program_data = json.dumps(program.to_dict())
                signature_data = json.dumps(program.signature)
                
                conn.execute("""
                    INSERT OR REPLACE INTO latent_programs (
                        id, signature_hash, signature_data, program_data,
                        created_at, last_used, usage_count, success_rate,
                        confidence_score, user_feedback_score, is_active,
                        is_experimental, version, parent_program_id,
                        avg_latency_ms, avg_token_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    program.id,
                    program.signature.get('signature_hash', ''),
                    signature_data,
                    program_data,
                    program.created_at.isoformat(),
                    program.last_used.isoformat(),
                    program.usage_count,
                    program.success_rate,
                    program.confidence_score,
                    program.user_feedback_score,
                    program.is_active,
                    program.is_experimental,
                    program.version,
                    program.parent_program_id,
                    program.avg_latency_ms,
                    program.avg_token_count
                ))
                
                conn.commit()
                logger.debug(f"Stored program {program.id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to store program {program.id}: {e}")
            return False
    
    def get_program(self, program_id: str) -> Optional[LatentProgram]:
        """Retrieve a specific program by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT program_data FROM latent_programs WHERE id = ? AND is_active = 1",
                    (program_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    program_data = json.loads(row[0])
                    return LatentProgram.from_dict(program_data)
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve program {program_id}: {e}")
            return None
    
    def find_similar_programs(self, signature: ProgramSignature, 
                            similarity_threshold: float = 0.8,
                            max_results: int = 5) -> List[LatentProgram]:
        """Find programs with similar signatures."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # First, get all active programs
                cursor = conn.execute("""
                    SELECT program_data, signature_data FROM latent_programs 
                    WHERE is_active = 1 
                    ORDER BY confidence_score DESC, usage_count DESC
                """)
                
                similar_programs = []
                
                for row in cursor.fetchall():
                    try:
                        program_data = json.loads(row[0])
                        signature_data = json.loads(row[1])
                        
                        # Create signature object for comparison
                        stored_signature = ProgramSignature.from_dict(signature_data)
                        
                        # Calculate similarity
                        similarity = signature.calculate_similarity(stored_signature)
                        
                        if similarity >= similarity_threshold:
                            program = LatentProgram.from_dict(program_data)
                            program.similarity_score = similarity  # Add similarity for ranking
                            similar_programs.append(program)
                            
                    except Exception as e:
                        logger.warning(f"Error processing program in similarity search: {e}")
                        continue
                
                # Sort by similarity and confidence, return top results
                similar_programs.sort(
                    key=lambda p: (p.similarity_score, p.confidence_score), 
                    reverse=True
                )
                
                return similar_programs[:max_results]
                
        except Exception as e:
            logger.error(f"Failed to find similar programs: {e}")
            return []
    
    def get_programs_by_signature_hash(self, signature_hash: str) -> List[LatentProgram]:
        """Get programs with exact signature hash match."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT program_data FROM latent_programs 
                    WHERE signature_hash = ? AND is_active = 1
                    ORDER BY confidence_score DESC
                """, (signature_hash,))
                
                programs = []
                for row in cursor.fetchall():
                    program_data = json.loads(row[0])
                    programs.append(LatentProgram.from_dict(program_data))
                
                return programs
                
        except Exception as e:
            logger.error(f"Failed to get programs by signature hash: {e}")
            return []
    
    def update_program_performance(self, program_id: str, execution_time_ms: float,
                                 token_count: int, success: bool = True,
                                 quality_score: Optional[float] = None,
                                 user_feedback: Optional[float] = None) -> bool:
        """Update program performance metrics."""
        try:
            # First, record the execution
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO program_executions (
                        program_id, executed_at, execution_time_ms, token_count,
                        success, quality_score, user_feedback
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    program_id,
                    datetime.utcnow().isoformat(),
                    execution_time_ms,
                    token_count,
                    success,
                    quality_score,
                    user_feedback
                ))
                
                # Update the program's aggregated metrics
                program = self.get_program(program_id)
                if program:
                    program.update_performance_metrics(
                        execution_time_ms, token_count, success, user_feedback
                    )
                    return self.store_program(program)
                
                return False
                
        except Exception as e:
            logger.error(f"Failed to update program performance: {e}")
            return False
    
    def retire_program(self, program_id: str) -> bool:
        """Mark a program as inactive (retired)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE latent_programs SET is_active = 0 WHERE id = ?",
                    (program_id,)
                )
                conn.commit()
                logger.info(f"Retired program {program_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to retire program {program_id}: {e}")
            return False
    
    def get_all_programs(self, include_inactive: bool = False) -> List[LatentProgram]:
        """Get all programs from the store."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT program_data FROM latent_programs"
                if not include_inactive:
                    query += " WHERE is_active = 1"
                query += " ORDER BY last_used DESC"
                
                cursor = conn.execute(query)
                programs = []
                
                for row in cursor.fetchall():
                    program_data = json.loads(row[0])
                    programs.append(LatentProgram.from_dict(program_data))
                
                return programs
                
        except Exception as e:
            logger.error(f"Failed to get all programs: {e}")
            return []
    
    def get_program_statistics(self) -> Dict[str, Any]:
        """Get statistics about the program store."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Basic counts
                cursor = conn.execute("SELECT COUNT(*) FROM latent_programs WHERE is_active = 1")
                active_count = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM latent_programs WHERE is_experimental = 1 AND is_active = 1")
                experimental_count = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT AVG(confidence_score) FROM latent_programs WHERE is_active = 1")
                avg_confidence = cursor.fetchone()[0] or 0.0
                
                cursor = conn.execute("SELECT SUM(usage_count) FROM latent_programs WHERE is_active = 1")
                total_usage = cursor.fetchone()[0] or 0
                
                cursor = conn.execute("SELECT AVG(avg_latency_ms) FROM latent_programs WHERE is_active = 1")
                avg_latency = cursor.fetchone()[0] or 0.0
                
                return {
                    'active_programs': active_count,
                    'experimental_programs': experimental_count,
                    'proven_programs': active_count - experimental_count,
                    'average_confidence': avg_confidence,
                    'total_usage': total_usage,
                    'average_latency_ms': avg_latency
                }
                
        except Exception as e:
            logger.error(f"Failed to get program statistics: {e}")
            return {}
    
    def cleanup_old_programs(self, days_unused: int = 30) -> int:
        """Remove programs that haven't been used in specified days."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_unused)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM latent_programs 
                    WHERE last_used < ? AND usage_count < 5
                """, (cutoff_date.isoformat(),))
                
                count = cursor.fetchone()[0]
                
                conn.execute("""
                    DELETE FROM latent_programs 
                    WHERE last_used < ? AND usage_count < 5
                """, (cutoff_date.isoformat(),))
                
                conn.commit()
                logger.info(f"Cleaned up {count} old programs")
                return count
                
        except Exception as e:
            logger.error(f"Failed to cleanup old programs: {e}")
            return 0
