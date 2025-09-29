"""
System Controller for managing application operations.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime


class SystemController:
    """
    Main controller class for managing system operations and coordinating
    between different components.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the SystemController.
        
        Args:
            config: Configuration dictionary for the controller
        """
        self.config = config
        self.name = config.get("name", "SystemController")
        self.version = config.get("version", "1.0.0")
        self.debug = config.get("debug", False)
        self.max_retries = config.get("max_retries", 3)
        self.timeout = config.get("timeout", 30)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Initialized {self.name} v{self.version}")
        
        # Track execution state
        self.execution_history = []
        self.current_status = "idle"
    
    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a parsed action.
        
        Args:
            action: Parsed action dictionary
            
        Returns:
            Result dictionary with execution status and data
        """
        self.logger.info(f"Executing action: {action.get('type', 'unknown')}")
        
        start_time = datetime.now()
        self.current_status = "executing"
        
        try:
            # Validate action
            if not self._validate_action(action):
                raise ValueError("Invalid action format")
            
            # Execute the action based on type
            result = self._process_action(action)
            
            # Record execution
            execution_record = {
                "action": action,
                "result": result,
                "timestamp": start_time,
                "duration": (datetime.now() - start_time).total_seconds(),
                "status": "success"
            }
            self.execution_history.append(execution_record)
            
            self.current_status = "idle"
            self.logger.info(f"Action executed successfully in {execution_record['duration']:.2f}s")
            
            return {
                "status": "success",
                "data": result,
                "timestamp": start_time.isoformat(),
                "duration": execution_record["duration"]
            }
            
        except Exception as e:
            error_record = {
                "action": action,
                "error": str(e),
                "timestamp": start_time,
                "duration": (datetime.now() - start_time).total_seconds(),
                "status": "error"
            }
            self.execution_history.append(error_record)
            self.current_status = "error"
            
            self.logger.error(f"Action execution failed: {e}")
            
            return {
                "status": "error",
                "error": str(e),
                "timestamp": start_time.isoformat(),
                "duration": error_record["duration"]
            }
    
    def _validate_action(self, action: Dict[str, Any]) -> bool:
        """
        Validate action format and requirements.
        
        Args:
            action: Action dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["type"]
        
        for field in required_fields:
            if field not in action:
                self.logger.warning(f"Missing required field: {field}")
                return False
        
        return True
    
    def _process_action(self, action: Dict[str, Any]) -> Any:
        """
        Process the action based on its type.
        
        Args:
            action: Action dictionary to process
            
        Returns:
            Processing result
        """
        action_type = action.get("type")
        
        # Define action processors
        processors = {
            "sample": self._process_sample_action,
            "test": self._process_test_action,
            "status": self._process_status_action
        }
        
        processor = processors.get(action_type, self._process_default_action)
        return processor(action)
    
    def _process_sample_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Process a sample action."""
        data = action.get("data", "")
        return {
            "type": "sample_response",
            "original_data": data,
            "processed_at": datetime.now().isoformat(),
            "message": f"Processed sample data: {data}"
        }
    
    def _process_test_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Process a test action."""
        return {
            "type": "test_response",
            "message": "Test action processed successfully",
            "controller_status": self.get_status()
        }
    
    def _process_status_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Process a status request action."""
        # Temporarily store current status and set to idle for status check
        temp_status = self.current_status
        self.current_status = "idle"
        status = self.get_status()
        self.current_status = temp_status
        return status
    
    def _process_default_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Process unknown action types."""
        self.logger.warning(f"Unknown action type: {action.get('type')}")
        return {
            "type": "unknown_action_response",
            "message": f"Unknown action type: {action.get('type')}",
            "supported_types": ["sample", "test", "status"]
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current controller status.
        
        Returns:
            Status dictionary
        """
        return {
            "name": self.name,
            "version": self.version,
            "current_status": self.current_status,
            "execution_count": len(self.execution_history),
            "last_execution": self.execution_history[-1]["timestamp"].isoformat() if self.execution_history else None,
            "config": self.config
        }
    
    def get_execution_history(self) -> list:
        """
        Get execution history.
        
        Returns:
            List of execution records
        """
        return self.execution_history.copy()
    
    def reset(self) -> None:
        """Reset controller state."""
        self.execution_history.clear()
        self.current_status = "idle"
        self.logger.info("Controller state reset")