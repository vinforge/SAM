"""
Secure & Supervised Execution for SAM
Controlled execution of tools/scripts with user approval and safety measures.

Sprint 8 Task 2: Secure & Supervised Execution
"""

import logging
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class ExecutionMode(Enum):
    """Execution modes for tools."""
    SIMULATE = "simulate"
    EXECUTE = "execute"
    EXPLAIN = "explain"

class ApprovalStatus(Enum):
    """Approval status for tool execution."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_APPROVED = "auto_approved"

class ExecutionStatus(Enum):
    """Status of tool execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ExecutionRequest:
    """Request for tool execution."""
    request_id: str
    tool_id: str
    tool_name: str
    input_data: Dict[str, Any]
    execution_mode: ExecutionMode
    user_id: str
    session_id: str
    requires_approval: bool
    approval_status: ApprovalStatus
    created_at: str
    metadata: Dict[str, Any]

@dataclass
class ExecutionResult:
    """Result of tool execution."""
    request_id: str
    execution_id: str
    tool_id: str
    status: ExecutionStatus
    output: Any
    error_message: Optional[str]
    execution_time_ms: int
    started_at: str
    completed_at: Optional[str]
    logs: List[str]
    metadata: Dict[str, Any]

@dataclass
class ExecutionLog:
    """Log entry for tool execution."""
    log_id: str
    request_id: str
    execution_id: str
    tool_id: str
    user_id: str
    session_id: str
    input_data: Dict[str, Any]
    output_data: Any
    execution_mode: ExecutionMode
    success: bool
    execution_time_ms: int
    timestamp: str
    metadata: Dict[str, Any]

class SecureExecutor:
    """
    Secure and supervised tool execution manager.
    """
    
    def __init__(self, logs_directory: str = "execution_logs",
                 approval_callback: Optional[Callable] = None):
        """
        Initialize the secure executor.
        
        Args:
            logs_directory: Directory for execution logs
            approval_callback: Function to call for user approval
        """
        self.logs_dir = Path(logs_directory)
        self.logs_dir.mkdir(exist_ok=True)
        
        self.approval_callback = approval_callback
        
        # Storage
        self.pending_requests: Dict[str, ExecutionRequest] = {}
        self.execution_results: Dict[str, ExecutionResult] = {}
        self.execution_logs: List[ExecutionLog] = []
        
        # Configuration
        self.config = {
            'auto_approve_safe_tools': True,
            'max_execution_time': 300,  # 5 minutes
            'log_all_executions': True,
            'sandbox_enabled': True
        }
        
        # Load existing logs
        self._load_execution_logs()
        
        logger.info(f"Secure executor initialized with logs in {logs_directory}")
    
    def submit_execution_request(self, tool_id: str, tool_name: str,
                                input_data: Dict[str, Any], execution_mode: ExecutionMode,
                                user_id: str, session_id: str,
                                requires_approval: bool = False,
                                metadata: Dict[str, Any] = None) -> str:
        """
        Submit a tool execution request.
        
        Args:
            tool_id: Tool ID to execute
            tool_name: Tool name
            input_data: Input data for the tool
            execution_mode: Execution mode
            user_id: User requesting execution
            session_id: Session ID
            requires_approval: Whether approval is required
            metadata: Additional metadata
            
        Returns:
            Request ID
        """
        try:
            request_id = f"req_{uuid.uuid4().hex[:12]}"
            
            # Determine approval status
            approval_status = ApprovalStatus.PENDING
            if not requires_approval and self.config['auto_approve_safe_tools']:
                approval_status = ApprovalStatus.AUTO_APPROVED
            
            request = ExecutionRequest(
                request_id=request_id,
                tool_id=tool_id,
                tool_name=tool_name,
                input_data=input_data,
                execution_mode=execution_mode,
                user_id=user_id,
                session_id=session_id,
                requires_approval=requires_approval,
                approval_status=approval_status,
                created_at=datetime.now().isoformat(),
                metadata=metadata or {}
            )
            
            self.pending_requests[request_id] = request
            
            logger.info(f"Submitted execution request: {tool_name} ({request_id})")
            
            # Auto-execute if approved
            if approval_status == ApprovalStatus.AUTO_APPROVED:
                return self._execute_request(request_id)
            
            return request_id
            
        except Exception as e:
            logger.error(f"Error submitting execution request: {e}")
            raise
    
    def approve_request(self, request_id: str, approved: bool = True) -> bool:
        """
        Approve or reject an execution request.
        
        Args:
            request_id: Request ID
            approved: Whether to approve the request
            
        Returns:
            True if successful, False otherwise
        """
        try:
            request = self.pending_requests.get(request_id)
            if not request:
                logger.error(f"Request not found: {request_id}")
                return False
            
            if approved:
                request.approval_status = ApprovalStatus.APPROVED
                logger.info(f"Approved execution request: {request_id}")
                
                # Execute the request
                self._execute_request(request_id)
            else:
                request.approval_status = ApprovalStatus.REJECTED
                logger.info(f"Rejected execution request: {request_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error approving request {request_id}: {e}")
            return False
    
    def get_execution_result(self, request_id: str) -> Optional[ExecutionResult]:
        """Get execution result by request ID."""
        return self.execution_results.get(request_id)
    
    def get_pending_requests(self, user_id: Optional[str] = None) -> List[ExecutionRequest]:
        """Get pending execution requests."""
        pending = [req for req in self.pending_requests.values() 
                  if req.approval_status == ApprovalStatus.PENDING]
        
        if user_id:
            pending = [req for req in pending if req.user_id == user_id]
        
        return pending
    
    def simulate_execution(self, tool_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate tool execution without actually running it.
        
        Args:
            tool_id: Tool ID to simulate
            input_data: Input data for simulation
            
        Returns:
            Simulated output
        """
        try:
            logger.info(f"Simulating execution of tool: {tool_id}")
            
            # Tool-specific simulation
            if tool_id == 'python_interpreter':
                return self._simulate_python_execution(input_data)
            elif tool_id == 'table_generator':
                return self._simulate_table_generation(input_data)
            elif tool_id == 'multimodal_query':
                return self._simulate_multimodal_query(input_data)
            elif tool_id == 'web_search':
                return self._simulate_web_search(input_data)
            else:
                return {
                    'simulated': True,
                    'tool_id': tool_id,
                    'input_processed': input_data,
                    'estimated_output': f"Simulated output from {tool_id}",
                    'execution_time_estimate': 3.0
                }
            
        except Exception as e:
            logger.error(f"Error simulating execution: {e}")
            return {'error': str(e), 'simulated': True}
    
    def explain_execution(self, tool_id: str, input_data: Dict[str, Any]) -> str:
        """
        Explain what a tool execution would do.
        
        Args:
            tool_id: Tool ID to explain
            input_data: Input data for explanation
            
        Returns:
            Explanation text
        """
        try:
            explanations = {
                'python_interpreter': f"Execute Python code: {input_data.get('code', 'No code provided')[:100]}...",
                'table_generator': f"Generate a table from data: {len(input_data.get('data', []))} rows",
                'multimodal_query': f"Search for information about: {input_data.get('query', 'No query')}",
                'web_search': f"Search the web for: {input_data.get('query', 'No query')}"
            }
            
            explanation = explanations.get(tool_id, f"Execute tool {tool_id} with provided input")
            
            logger.info(f"Generated explanation for {tool_id}")
            return explanation
            
        except Exception as e:
            logger.error(f"Error explaining execution: {e}")
            return f"Error explaining tool {tool_id}: {str(e)}"
    
    def _execute_request(self, request_id: str) -> str:
        """Execute an approved request."""
        try:
            request = self.pending_requests.get(request_id)
            if not request:
                raise ValueError(f"Request not found: {request_id}")
            
            if request.approval_status not in [ApprovalStatus.APPROVED, ApprovalStatus.AUTO_APPROVED]:
                raise ValueError(f"Request not approved: {request_id}")
            
            execution_id = f"exec_{uuid.uuid4().hex[:12]}"
            start_time = datetime.now()
            
            logger.info(f"Executing request: {request.tool_name} ({execution_id})")
            
            # Create execution result
            result = ExecutionResult(
                request_id=request_id,
                execution_id=execution_id,
                tool_id=request.tool_id,
                status=ExecutionStatus.RUNNING,
                output=None,
                error_message=None,
                execution_time_ms=0,
                started_at=start_time.isoformat(),
                completed_at=None,
                logs=[],
                metadata={}
            )
            
            self.execution_results[request_id] = result
            
            try:
                # Execute based on mode
                if request.execution_mode == ExecutionMode.SIMULATE:
                    output = self.simulate_execution(request.tool_id, request.input_data)
                elif request.execution_mode == ExecutionMode.EXPLAIN:
                    output = self.explain_execution(request.tool_id, request.input_data)
                elif request.execution_mode == ExecutionMode.EXECUTE:
                    output = self._actual_tool_execution(request.tool_id, request.input_data)
                else:
                    raise ValueError(f"Unknown execution mode: {request.execution_mode}")
                
                # Update result
                end_time = datetime.now()
                execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
                
                result.status = ExecutionStatus.COMPLETED
                result.output = output
                result.execution_time_ms = execution_time_ms
                result.completed_at = end_time.isoformat()
                result.logs.append(f"Execution completed successfully in {execution_time_ms}ms")
                
                logger.info(f"Execution completed: {execution_id} ({execution_time_ms}ms)")
                
            except Exception as e:
                # Handle execution error
                end_time = datetime.now()
                execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
                
                result.status = ExecutionStatus.FAILED
                result.error_message = str(e)
                result.execution_time_ms = execution_time_ms
                result.completed_at = end_time.isoformat()
                result.logs.append(f"Execution failed: {str(e)}")
                
                logger.error(f"Execution failed: {execution_id} - {str(e)}")
            
            # Log execution
            self._log_execution(request, result)
            
            # Remove from pending
            if request_id in self.pending_requests:
                del self.pending_requests[request_id]
            
            return execution_id
            
        except Exception as e:
            logger.error(f"Error executing request {request_id}: {e}")
            raise
    
    def _actual_tool_execution(self, tool_id: str, input_data: Dict[str, Any]) -> Any:
        """Perform actual tool execution (placeholder for real implementations)."""
        # This would integrate with actual tool implementations
        # For now, return simulated results
        logger.warning(f"Actual execution not implemented for {tool_id}, returning simulation")
        return self.simulate_execution(tool_id, input_data)
    
    def _simulate_python_execution(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Python code execution."""
        code = input_data.get('code', '')
        
        return {
            'simulated': True,
            'code_analyzed': code[:200] + '...' if len(code) > 200 else code,
            'estimated_output': 'Code execution result would appear here',
            'variables_created': ['result', 'data'],
            'imports_detected': ['math', 'numpy'] if 'import' in code else [],
            'execution_safe': 'dangerous' not in code.lower()
        }
    
    def _simulate_table_generation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate table generation."""
        data = input_data.get('data', [])
        
        return {
            'simulated': True,
            'table_rows': len(data) if isinstance(data, list) else 0,
            'table_columns': len(data[0]) if data and isinstance(data[0], (list, dict)) else 0,
            'table_format': 'markdown',
            'estimated_output': '| Column 1 | Column 2 |\n|----------|----------|\n| Data     | Data     |'
        }
    
    def _simulate_multimodal_query(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate multimodal query execution."""
        query = input_data.get('query', '')
        
        return {
            'simulated': True,
            'query_processed': query,
            'estimated_results': 3,
            'search_domains': ['documents', 'knowledge_base'],
            'estimated_relevance': 0.85
        }
    
    def _simulate_web_search(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate web search execution."""
        query = input_data.get('query', '')
        
        return {
            'simulated': True,
            'search_query': query,
            'estimated_results': 5,
            'search_engines': ['google', 'bing'],
            'estimated_response_time': 2.5
        }
    
    def _log_execution(self, request: ExecutionRequest, result: ExecutionResult):
        """Log execution for audit trail."""
        try:
            log_entry = ExecutionLog(
                log_id=f"log_{uuid.uuid4().hex[:12]}",
                request_id=request.request_id,
                execution_id=result.execution_id,
                tool_id=request.tool_id,
                user_id=request.user_id,
                session_id=request.session_id,
                input_data=request.input_data,
                output_data=result.output,
                execution_mode=request.execution_mode,
                success=result.status == ExecutionStatus.COMPLETED,
                execution_time_ms=result.execution_time_ms,
                timestamp=datetime.now().isoformat(),
                metadata={
                    'tool_name': request.tool_name,
                    'requires_approval': request.requires_approval,
                    'approval_status': request.approval_status.value,
                    'error_message': result.error_message
                }
            )
            
            self.execution_logs.append(log_entry)
            
            # Save to file
            if self.config['log_all_executions']:
                self._save_execution_log(log_entry)
            
            logger.debug(f"Logged execution: {log_entry.log_id}")
            
        except Exception as e:
            logger.error(f"Error logging execution: {e}")
    
    def _save_execution_log(self, log_entry: ExecutionLog):
        """Save execution log to file."""
        try:
            log_file = self.logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}_executions.jsonl"
            
            log_dict = asdict(log_entry)
            log_dict['execution_mode'] = log_entry.execution_mode.value
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_dict) + '\n')
            
        except Exception as e:
            logger.error(f"Error saving execution log: {e}")
    
    def _load_execution_logs(self):
        """Load recent execution logs."""
        try:
            # Load logs from the last 7 days
            for log_file in self.logs_dir.glob("*_executions.jsonl"):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                log_data = json.loads(line)
                                log_entry = ExecutionLog(
                                    log_id=log_data['log_id'],
                                    request_id=log_data['request_id'],
                                    execution_id=log_data['execution_id'],
                                    tool_id=log_data['tool_id'],
                                    user_id=log_data['user_id'],
                                    session_id=log_data['session_id'],
                                    input_data=log_data['input_data'],
                                    output_data=log_data['output_data'],
                                    execution_mode=ExecutionMode(log_data['execution_mode']),
                                    success=log_data['success'],
                                    execution_time_ms=log_data['execution_time_ms'],
                                    timestamp=log_data['timestamp'],
                                    metadata=log_data['metadata']
                                )
                                self.execution_logs.append(log_entry)
                except Exception as e:
                    logger.warning(f"Error loading log file {log_file}: {e}")
            
            logger.info(f"Loaded {len(self.execution_logs)} execution logs")
            
        except Exception as e:
            logger.error(f"Error loading execution logs: {e}")
    
    def get_execution_stats(self, user_id: Optional[str] = None, 
                           days_back: int = 7) -> Dict[str, Any]:
        """Get execution statistics."""
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # Filter logs
            relevant_logs = []
            for log in self.execution_logs:
                log_date = datetime.fromisoformat(log.timestamp)
                if log_date >= cutoff_date:
                    if user_id is None or log.user_id == user_id:
                        relevant_logs.append(log)
            
            # Calculate statistics
            total_executions = len(relevant_logs)
            successful_executions = sum(1 for log in relevant_logs if log.success)
            
            tool_usage = {}
            execution_modes = {}
            
            for log in relevant_logs:
                # Tool usage
                tool_usage[log.tool_id] = tool_usage.get(log.tool_id, 0) + 1
                
                # Execution modes
                mode = log.execution_mode.value
                execution_modes[mode] = execution_modes.get(mode, 0) + 1
            
            return {
                'total_executions': total_executions,
                'successful_executions': successful_executions,
                'success_rate': successful_executions / total_executions if total_executions > 0 else 0,
                'tool_usage': tool_usage,
                'execution_modes': execution_modes,
                'period_days': days_back
            }
            
        except Exception as e:
            logger.error(f"Error getting execution stats: {e}")
            return {}

# Global secure executor instance
_secure_executor = None

def get_secure_executor(logs_directory: str = "execution_logs",
                       approval_callback: Optional[Callable] = None) -> SecureExecutor:
    """Get or create a global secure executor instance."""
    global _secure_executor
    
    if _secure_executor is None:
        _secure_executor = SecureExecutor(
            logs_directory=logs_directory,
            approval_callback=approval_callback
        )
    
    return _secure_executor
