"""
MEMOIR Edit Skill

Implementation of the MEMOIR editing skill for localized model updates.
This skill performs the "write" operation in the MEMOIR framework,
allowing for non-destructive knowledge editing and lifelong learning.

Based on the MEMOIR paper: "Localized Model Editing for Lifelong Learning"
Author: SAM Development Team
Version: 1.0.0
"""

import torch
import torch.nn as nn
import torch.optim as optim
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import uuid

from ..base import BaseSkillModule, SkillExecutionError, SkillDependencyError
from ...uif import SAM_UIF, UIFStatus
from ....core.model_layers import ResidualMemoryLayer, MEMOIRTransformerBlock
from ....core.fingerprinter import TopHashFingerprinter
from ....memory.edit_mask_db import EditMaskDatabase
from ....core.diagnostics import GradientLogger, GradientHealthMonitor

logger = logging.getLogger(__name__)

class MEMOIR_EditSkill(BaseSkillModule):
    """
    MEMOIR Edit Skill for performing localized model edits.
    
    This skill implements the "write" operation from the MEMOIR paper,
    enabling non-destructive knowledge updates through sparse residual
    connections. It performs gradient-isolated training to update only
    the relevant neurons for a specific edit.
    
    Key Features:
    - Localized gradient updates using edit masks
    - Integration with TopHashFingerprinter for mask generation
    - Storage in EditMaskDatabase for retrieval
    - Comprehensive validation and error handling
    - Performance monitoring and optimization
    """
    
    # Skill identification
    skill_name = "MEMOIR_EditSkill"
    skill_version = "1.0.0"
    skill_description = "Updates the model's internal knowledge with new or corrected facts using MEMOIR framework"
    skill_category = "internal"
    
    # Dependency declarations
    required_inputs = ["edit_prompt", "correct_answer"]
    optional_inputs = ["edit_context", "confidence_score", "edit_metadata"]
    output_keys = ["edit_id", "edit_success", "edit_mask", "training_metrics"]
    
    # Skill characteristics
    requires_external_access = False
    requires_vetting = False
    can_run_parallel = False  # Model editing should be sequential
    estimated_execution_time = 2.0  # Estimated 2 seconds per edit
    max_execution_time = 30.0  # Maximum 30 seconds
    
    def __init__(
        self,
        model: Optional[nn.Module] = None,
        target_layer_name: str = "memoir_layer",
        hidden_size: int = 4096,
        learning_rate: float = 1e-4,
        max_training_steps: int = 10,
        convergence_threshold: float = 1e-5,
        fingerprinter: Optional[TopHashFingerprinter] = None,
        mask_database: Optional[EditMaskDatabase] = None
    ):
        """
        Initialize the MEMOIR Edit Skill.
        
        Args:
            model: The model to edit (will be detected if None)
            target_layer_name: Name of the layer to edit
            hidden_size: Hidden dimension size
            learning_rate: Learning rate for gradient updates
            max_training_steps: Maximum training iterations
            convergence_threshold: Convergence threshold for training
            fingerprinter: TopHashFingerprinter instance
            mask_database: EditMaskDatabase instance
        """
        super().__init__()
        
        self.model = model
        self.target_layer_name = target_layer_name
        self.hidden_size = hidden_size
        self.learning_rate = learning_rate
        self.max_training_steps = max_training_steps
        self.convergence_threshold = convergence_threshold
        
        # Initialize MEMOIR components
        self.fingerprinter = fingerprinter or TopHashFingerprinter(
            hidden_size=hidden_size,
            top_k=max(50, hidden_size // 100),  # 1% sparsity by default
            permutation_file="data/memoir_permutation.pkl"
        )
        
        self.mask_database = mask_database or EditMaskDatabase(
            hidden_size=hidden_size,
            storage_dir="data/memoir_masks"
        )
        
        # Training state
        self.edit_count = 0
        self.successful_edits = 0
        self.failed_edits = 0
        
        # Performance tracking
        self.training_metrics = {
            'total_edits': 0,
            'successful_edits': 0,
            'average_training_time': 0.0,
            'average_convergence_steps': 0.0
        }

        # Gradient health monitoring
        self.gradient_monitor = GradientHealthMonitor(
            vanishing_threshold=1e-7,
            exploding_threshold=100.0,
            noise_window=10,
            stall_window=5
        )

        logger.info(f"MEMOIR_EditSkill initialized with hidden_size={hidden_size}")
    
    def execute(self, uif: SAM_UIF) -> SAM_UIF:
        """
        Execute the MEMOIR edit operation.
        
        Args:
            uif: Universal Interface Format with edit parameters
            
        Returns:
            Updated UIF with edit results
        """
        try:
            # Extract edit parameters
            edit_prompt = uif.intermediate_data["edit_prompt"]
            correct_answer = uif.intermediate_data["correct_answer"]
            edit_context = uif.intermediate_data.get("edit_context", "")
            confidence_score = uif.intermediate_data.get("confidence_score", 1.0)
            edit_metadata = uif.intermediate_data.get("edit_metadata", {})
            
            # Generate unique edit ID
            edit_id = f"edit_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
            
            # Log edit attempt
            uif.add_log_entry(f"Starting MEMOIR edit: {edit_id}", self.skill_name)
            uif.add_log_entry(f"Edit prompt: {edit_prompt[:100]}...", self.skill_name)
            
            # Perform the edit
            edit_result = self._perform_edit(
                edit_id=edit_id,
                edit_prompt=edit_prompt,
                correct_answer=correct_answer,
                edit_context=edit_context,
                confidence_score=confidence_score,
                edit_metadata=edit_metadata
            )
            
            # Store results in UIF
            uif.intermediate_data["edit_id"] = edit_id
            uif.intermediate_data["edit_success"] = edit_result["success"]
            uif.intermediate_data["edit_mask"] = edit_result["edit_mask"]
            uif.intermediate_data["training_metrics"] = edit_result["training_metrics"]
            
            # Set skill outputs
            uif.set_skill_output(self.skill_name, {
                "edit_id": edit_id,
                "success": edit_result["success"],
                "training_steps": edit_result["training_metrics"]["steps"],
                "final_loss": edit_result["training_metrics"]["final_loss"],
                "convergence_achieved": edit_result["training_metrics"]["converged"]
            })
            
            if edit_result["success"]:
                self.successful_edits += 1
                uif.add_log_entry(f"MEMOIR edit completed successfully", self.skill_name)

                # Add gradient health information if available
                training_metrics = edit_result.get("training_metrics", {})
                if "gradient_pathology" in training_metrics:
                    pathology = training_metrics["gradient_pathology"]
                    if pathology != "healthy":
                        uif.add_log_entry(f"Gradient health: {pathology}", self.skill_name)
            else:
                self.failed_edits += 1
                error_msg = edit_result.get('error', 'Unknown error')

                # Enhanced error reporting with gradient health information
                training_metrics = edit_result.get("training_metrics", {})
                if "gradient_health" in training_metrics:
                    health_report = training_metrics["gradient_health"]
                    if health_report and health_report.pathology.value != "healthy":
                        error_msg += f" | Gradient issue: {health_report.description}"
                        uif.error_details = {
                            "gradient_pathology": health_report.pathology.value,
                            "gradient_severity": health_report.severity,
                            "gradient_recommendations": health_report.recommendations,
                            "original_error": edit_result.get('error', 'Unknown error')
                        }

                uif.add_warning(f"MEMOIR edit failed: {error_msg}")
            
            self.edit_count += 1
            
            return uif
            
        except Exception as e:
            self.logger.exception(f"MEMOIR edit failed: {e}")
            raise SkillExecutionError(f"MEMOIR edit execution failed: {str(e)}")
    
    def _perform_edit(
        self,
        edit_id: str,
        edit_prompt: str,
        correct_answer: str,
        edit_context: str = "",
        confidence_score: float = 1.0,
        edit_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Perform the actual MEMOIR edit operation.
        
        Args:
            edit_id: Unique identifier for this edit
            edit_prompt: The prompt that should trigger the correction
            correct_answer: The correct answer to learn
            edit_context: Additional context for the edit
            confidence_score: Confidence in the correction
            edit_metadata: Additional metadata
            
        Returns:
            Dictionary with edit results
        """
        try:
            # Step 1: Get model and target layer
            target_layer = self._get_target_layer()
            if target_layer is None:
                return {
                    "success": False,
                    "error": "Target layer not found",
                    "edit_mask": None,
                    "training_metrics": {}
                }
            
            # Step 2: Generate activations for the edit prompt
            activations = self._generate_activations(edit_prompt, edit_context)
            
            # Step 3: Generate edit mask using fingerprinter
            edit_mask = self.fingerprinter.generate_mask(activations)
            
            # Step 4: Check for similar existing edits
            similar_edit = self.mask_database.find_closest(edit_mask, threshold=0.8)
            if similar_edit:
                existing_id, existing_mask, similarity = similar_edit
                logger.info(f"Found similar edit {existing_id} with similarity {similarity:.3f}")
                # Could merge or update existing edit here
            
            # Step 5: Perform gradient-isolated training
            training_metrics = self._train_edit(
                target_layer=target_layer,
                edit_mask=edit_mask,
                edit_prompt=edit_prompt,
                correct_answer=correct_answer,
                edit_context=edit_context
            )
            
            # Step 6: Store edit in database
            metadata = {
                "edit_prompt": edit_prompt,
                "correct_answer": correct_answer,
                "edit_context": edit_context,
                "confidence_score": confidence_score,
                "training_metrics": training_metrics,
                **(edit_metadata or {})
            }
            
            success = self.mask_database.add(edit_id, edit_mask, metadata)
            if not success:
                return {
                    "success": False,
                    "error": "Failed to store edit in database",
                    "edit_mask": edit_mask,
                    "training_metrics": training_metrics
                }
            
            # Step 7: Add edit to target layer
            slot = target_layer.add_edit(edit_id, edit_mask, metadata)
            if slot is None:
                return {
                    "success": False,
                    "error": "Failed to add edit to target layer",
                    "edit_mask": edit_mask,
                    "training_metrics": training_metrics
                }
            
            return {
                "success": True,
                "edit_mask": edit_mask,
                "training_metrics": training_metrics,
                "slot": slot
            }
            
        except Exception as e:
            logger.exception(f"Error performing MEMOIR edit: {e}")
            return {
                "success": False,
                "error": str(e),
                "edit_mask": None,
                "training_metrics": {}
            }
    
    def _get_target_layer(self) -> Optional[ResidualMemoryLayer]:
        """
        Get the target ResidualMemoryLayer for editing.
        
        Returns:
            ResidualMemoryLayer instance or None if not found
        """
        if self.model is None:
            # Try to get model from global context or SAM instance
            logger.warning("No model provided, attempting to detect automatically")
            return None
        
        # Search for MEMOIR-enabled layers
        for name, module in self.model.named_modules():
            if isinstance(module, MEMOIRTransformerBlock) and module.residual_memory is not None:
                logger.info(f"Found MEMOIR layer: {name}")
                return module.residual_memory
            elif isinstance(module, ResidualMemoryLayer):
                logger.info(f"Found ResidualMemoryLayer: {name}")
                return module
        
        logger.warning("No MEMOIR-enabled layers found in model")
        return None
    
    def _generate_activations(self, edit_prompt: str, edit_context: str = "") -> torch.Tensor:
        """
        Generate activations for the edit prompt.
        
        Args:
            edit_prompt: The prompt to generate activations for
            edit_context: Additional context
            
        Returns:
            Activation tensor
        """
        # For now, generate synthetic activations
        # In a real implementation, this would run the prompt through the model
        # to get activations from the layer preceding the target layer
        
        combined_text = f"{edit_context} {edit_prompt}".strip()
        
        # Generate deterministic activations based on text content
        # This is a placeholder - real implementation would use actual model forward pass
        torch.manual_seed(hash(combined_text) % 2**32)
        activations = torch.randn(self.hidden_size)
        
        # Add some structure based on text characteristics
        text_hash = hash(combined_text)
        for i in range(0, self.hidden_size, 100):
            if (text_hash >> (i // 100)) & 1:
                activations[i:i+10] *= 2.0
        
        return activations
    
    def _train_edit(
        self,
        target_layer: ResidualMemoryLayer,
        edit_mask: torch.Tensor,
        edit_prompt: str,
        correct_answer: str,
        edit_context: str = ""
    ) -> Dict[str, Any]:
        """
        Perform gradient-isolated training for the edit.
        
        Args:
            target_layer: The layer to train
            edit_mask: Sparse mask for the edit
            edit_prompt: Edit prompt
            correct_answer: Correct answer
            edit_context: Additional context
            
        Returns:
            Training metrics
        """
        # Find the edit slot that was just added
        edit_slots = torch.where(target_layer.edit_active)[0]
        if len(edit_slots) == 0:
            return {"steps": 0, "final_loss": float('inf'), "converged": False}
        
        current_slot = edit_slots[-1].item()  # Use the most recently added slot
        
        # Set up optimizer for only the current edit slot
        edit_params = [target_layer.edit_weights[current_slot]]
        optimizer = optim.Adam(edit_params, lr=self.learning_rate)
        
        # Training loop with gradient monitoring
        training_metrics = {
            "steps": 0,
            "losses": [],
            "converged": False,
            "final_loss": float('inf'),
            "gradient_health": None,
            "gradient_pathology": None
        }

        # Initialize gradient logger for monitoring
        with GradientLogger(
            model=target_layer,
            target_layers=['edit_weights'],
            log_frequency=1
        ) as gradient_logger:

            for step in range(self.max_training_steps):
                optimizer.zero_grad()

                # Generate synthetic training data
                # In real implementation, this would be actual model forward/backward pass
                hidden_states = self._generate_activations(edit_prompt, edit_context)
                hidden_states = hidden_states.unsqueeze(0).unsqueeze(0)  # Add batch and sequence dims

                # Forward pass through residual memory layer
                residual_output = target_layer(
                    hidden_states,
                    edit_mask=edit_mask,
                    edit_id=None  # Use all active edits
                )

                # Compute loss (simplified - real implementation would use language modeling loss)
                target_activation = torch.ones_like(residual_output) * 0.1  # Target small positive activation
                loss = nn.MSELoss()(residual_output, target_activation)

                # Backward pass
                loss.backward()

                # Log gradient information for monitoring
                gradient_logger.log_step(
                    loss_value=loss.item(),
                    learning_rate=self.learning_rate
                )

                # Apply gradient only to the masked positions
                with torch.no_grad():
                    grad = target_layer.edit_weights.grad[current_slot]
                    masked_grad = grad * edit_mask
                    target_layer.edit_weights.grad[current_slot] = masked_grad

                optimizer.step()

                # Track metrics
                current_loss = loss.item()
                training_metrics["losses"].append(current_loss)
                training_metrics["steps"] = step + 1

                # Check convergence
                if current_loss < self.convergence_threshold:
                    training_metrics["converged"] = True
                    break

                # Check for improvement
                if step > 2 and len(training_metrics["losses"]) >= 3:
                    recent_losses = training_metrics["losses"][-3:]
                    if all(abs(recent_losses[i] - recent_losses[i-1]) < self.convergence_threshold
                           for i in range(1, len(recent_losses))):
                        training_metrics["converged"] = True
                        break

            # Analyze gradient health after training
            gradient_snapshots = gradient_logger.get_snapshots()
            if gradient_snapshots:
                health_report = self.gradient_monitor.analyze_gradient_health(gradient_snapshots)
                training_metrics["gradient_health"] = health_report
                training_metrics["gradient_pathology"] = health_report.pathology.value

                # Log gradient health summary
                health_summary = self.gradient_monitor.get_health_summary(health_report)
                logger.info(f"Gradient health analysis: {health_summary}")

                # If severe pathology detected, log detailed recommendations
                if health_report.severity > 0.7:
                    logger.warning(f"Severe gradient pathology detected: {health_report.description}")
                    for recommendation in health_report.recommendations:
                        logger.warning(f"  Recommendation: {recommendation}")
            else:
                logger.warning("No gradient snapshots captured during training")
        
        training_metrics["final_loss"] = training_metrics["losses"][-1] if training_metrics["losses"] else float('inf')
        
        logger.info(f"Training completed: {training_metrics['steps']} steps, "
                   f"final_loss={training_metrics['final_loss']:.6f}, "
                   f"converged={training_metrics['converged']}")
        
        return training_metrics
    
    def get_edit_statistics(self) -> Dict[str, Any]:
        """Get statistics about performed edits."""
        success_rate = self.successful_edits / max(self.edit_count, 1)
        
        return {
            "total_edits": self.edit_count,
            "successful_edits": self.successful_edits,
            "failed_edits": self.failed_edits,
            "success_rate": success_rate,
            "fingerprinter_stats": self.fingerprinter.get_statistics(),
            "database_stats": self.mask_database.get_statistics()
        }
    
    def validate_edit_parameters(self, uif: SAM_UIF) -> bool:
        """
        Validate that edit parameters are properly formatted.
        
        Args:
            uif: UIF to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            edit_prompt = uif.intermediate_data.get("edit_prompt")
            correct_answer = uif.intermediate_data.get("correct_answer")
            
            if not edit_prompt or not isinstance(edit_prompt, str):
                return False
            
            if not correct_answer or not isinstance(correct_answer, str):
                return False
            
            if len(edit_prompt.strip()) < 5:
                return False
            
            if len(correct_answer.strip()) < 1:
                return False
            
            return True
            
        except Exception:
            return False
    
    def can_execute(self, uif: SAM_UIF) -> bool:
        """
        Check if this skill can execute with the current UIF state.
        
        Args:
            uif: UIF to check
            
        Returns:
            True if skill can execute, False otherwise
        """
        # Check base dependencies
        if not super().can_execute(uif):
            return False
        
        # Check edit parameter validation
        return self.validate_edit_parameters(uif)
