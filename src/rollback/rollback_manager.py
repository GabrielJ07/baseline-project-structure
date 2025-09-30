"""
Rollback Manager for handling state changes and reversions.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from copy import deepcopy


@dataclass
class RollbackPoint:
    """Represents a point in time that can be rolled back to."""
    id: str
    timestamp: datetime
    description: str
    state_snapshot: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "state_snapshot": self.state_snapshot,
            "metadata": self.metadata
        }


class RollbackManager:
    """
    Manager class for handling rollback operations and state management.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the RollbackManager.
        
        Args:
            config: Configuration dictionary for the rollback manager
        """
        self.config = config
        self.enabled = config.get("enabled", True)
        self.max_history = config.get("max_history", 10)
        self.auto_cleanup = config.get("auto_cleanup", True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Initialized RollbackManager (enabled: {self.enabled}, max_history: {self.max_history})")
        
        # Rollback history
        self.rollback_points: List[RollbackPoint] = []
        self.current_state: Dict[str, Any] = {}
        
        # Statistics
        self.rollback_count = 0
        self.checkpoint_count = 0
    
    def create_checkpoint(self, description: str, state: Dict[str, Any], 
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a rollback checkpoint.
        
        Args:
            description: Description of the checkpoint
            state: Current state to save
            metadata: Optional metadata for the checkpoint
            
        Returns:
            Checkpoint ID
        """
        if not self.enabled:
            self.logger.warning("Rollback manager is disabled")
            return ""
        
        checkpoint_id = f"checkpoint_{self.checkpoint_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        rollback_point = RollbackPoint(
            id=checkpoint_id,
            timestamp=datetime.now(),
            description=description,
            state_snapshot=deepcopy(state),
            metadata=metadata or {}
        )
        
        self.rollback_points.append(rollback_point)
        self.current_state = deepcopy(state)
        self.checkpoint_count += 1
        
        # Cleanup old checkpoints if needed
        if self.auto_cleanup and len(self.rollback_points) > self.max_history:
            removed = self.rollback_points.pop(0)
            self.logger.debug(f"Removed old checkpoint: {removed.id}")
        
        self.logger.info(f"Created checkpoint: {checkpoint_id} - {description}")
        return checkpoint_id
    
    def rollback_to_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """
        Rollback to a specific checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint to rollback to
            
        Returns:
            State data if successful, None if failed
        """
        if not self.enabled:
            self.logger.warning("Rollback manager is disabled")
            return None
        
        # Find the checkpoint
        target_checkpoint = None
        for checkpoint in self.rollback_points:
            if checkpoint.id == checkpoint_id:
                target_checkpoint = checkpoint
                break
        
        if not target_checkpoint:
            self.logger.error(f"Checkpoint not found: {checkpoint_id}")
            return None
        
        try:
            # Restore state
            restored_state = deepcopy(target_checkpoint.state_snapshot)
            self.current_state = restored_state
            self.rollback_count += 1
            
            self.logger.info(f"Successfully rolled back to checkpoint: {checkpoint_id}")
            return restored_state
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            return None
    
    def rollback_to_latest(self) -> Optional[Dict[str, Any]]:
        """
        Rollback to the most recent checkpoint.
        
        Returns:
            State data if successful, None if failed
        """
        if not self.rollback_points:
            self.logger.warning("No checkpoints available for rollback")
            return None
        
        latest_checkpoint = max(self.rollback_points, key=lambda cp: cp.timestamp)
        return self.rollback_to_checkpoint(latest_checkpoint.id)
    
    def rollback_n_steps(self, steps: int) -> Optional[Dict[str, Any]]:
        """
        Rollback n steps from the current position.
        
        Args:
            steps: Number of steps to rollback
            
        Returns:
            State data if successful, None if failed
        """
        if not self.rollback_points:
            self.logger.warning("No checkpoints available for rollback")
            return None
        
        if steps <= 0 or steps > len(self.rollback_points):
            self.logger.error(f"Invalid rollback steps: {steps}")
            return None
        
        # Sort checkpoints by timestamp (newest first)
        sorted_checkpoints = sorted(self.rollback_points, key=lambda cp: cp.timestamp, reverse=True)
        target_checkpoint = sorted_checkpoints[steps - 1]
        
        return self.rollback_to_checkpoint(target_checkpoint.id)
    
    def get_checkpoint_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of checkpoints.
        
        Returns:
            List of checkpoint dictionaries
        """
        return [cp.to_dict() for cp in sorted(self.rollback_points, key=lambda cp: cp.timestamp, reverse=True)]
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details of a specific checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint
            
        Returns:
            Checkpoint dictionary or None if not found
        """
        for checkpoint in self.rollback_points:
            if checkpoint.id == checkpoint_id:
                return checkpoint.to_dict()
        return None
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Delete a specific checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint to delete
            
        Returns:
            True if deleted, False if not found
        """
        for i, checkpoint in enumerate(self.rollback_points):
            if checkpoint.id == checkpoint_id:
                removed = self.rollback_points.pop(i)
                self.logger.info(f"Deleted checkpoint: {removed.id}")
                return True
        
        self.logger.warning(f"Checkpoint not found for deletion: {checkpoint_id}")
        return False
    
    def clear_history(self) -> None:
        """Clear all rollback history."""
        cleared_count = len(self.rollback_points)
        self.rollback_points.clear()
        self.current_state.clear()
        self.logger.info(f"Cleared {cleared_count} checkpoints from history")
    
    def export_checkpoint(self, checkpoint_id: str, file_path: str) -> bool:
        """
        Export a checkpoint to a file.
        
        Args:
            checkpoint_id: ID of the checkpoint to export
            file_path: Path to save the checkpoint
            
        Returns:
            True if successful, False otherwise
        """
        checkpoint_data = self.get_checkpoint(checkpoint_id)
        if not checkpoint_data:
            return False
        
        try:
            with open(file_path, 'w') as f:
                json.dump(checkpoint_data, f, indent=2, default=str)
            
            self.logger.info(f"Exported checkpoint {checkpoint_id} to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export checkpoint: {e}")
            return False
    
    def import_checkpoint(self, file_path: str) -> Optional[str]:
        """
        Import a checkpoint from a file.
        
        Args:
            file_path: Path to the checkpoint file
            
        Returns:
            Checkpoint ID if successful, None otherwise
        """
        try:
            with open(file_path, 'r') as f:
                checkpoint_data = json.load(f)
            
            # Validate checkpoint data
            if not all(key in checkpoint_data for key in ['id', 'timestamp', 'description', 'state_snapshot']):
                raise ValueError("Invalid checkpoint format")
            
            # Create new rollback point
            rollback_point = RollbackPoint(
                id=checkpoint_data['id'],
                timestamp=datetime.fromisoformat(checkpoint_data['timestamp']),
                description=checkpoint_data['description'],
                state_snapshot=checkpoint_data['state_snapshot'],
                metadata=checkpoint_data.get('metadata', {})
            )
            
            self.rollback_points.append(rollback_point)
            self.logger.info(f"Imported checkpoint {rollback_point.id} from {file_path}")
            
            return rollback_point.id
            
        except Exception as e:
            self.logger.error(f"Failed to import checkpoint: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get rollback manager statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            "enabled": self.enabled,
            "total_checkpoints": len(self.rollback_points),
            "max_history": self.max_history,
            "rollback_count": self.rollback_count,
            "checkpoint_count": self.checkpoint_count,
            "oldest_checkpoint": min(self.rollback_points, key=lambda cp: cp.timestamp).timestamp.isoformat() if self.rollback_points else None,
            "newest_checkpoint": max(self.rollback_points, key=lambda cp: cp.timestamp).timestamp.isoformat() if self.rollback_points else None,
            "config": self.config
        }
    
    def validate_state_integrity(self) -> Dict[str, Any]:
        """
        Validate the integrity of stored states.
        
        Returns:
            Validation report
        """
        report = {
            "total_checkpoints": len(self.rollback_points),
            "valid_checkpoints": 0,
            "invalid_checkpoints": 0,
            "errors": []
        }
        
        for checkpoint in self.rollback_points:
            try:
                # Basic validation - ensure state_snapshot is serializable
                json.dumps(checkpoint.state_snapshot)
                report["valid_checkpoints"] += 1
            except Exception as e:
                report["invalid_checkpoints"] += 1
                report["errors"].append({
                    "checkpoint_id": checkpoint.id,
                    "error": str(e)
                })
        
        return report