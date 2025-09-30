"""
Unit tests for SystemController.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from controller.system_controller import SystemController


class TestSystemController(unittest.TestCase):
    """Test cases for SystemController class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "name": "TestController",
            "version": "1.0.0", 
            "debug": True,
            "max_retries": 3,
            "timeout": 30
        }
        self.controller = SystemController(self.config)
    
    def test_initialization(self):
        """Test controller initialization."""
        self.assertEqual(self.controller.name, "TestController")
        self.assertEqual(self.controller.version, "1.0.0")
        self.assertTrue(self.controller.debug)
        self.assertEqual(self.controller.max_retries, 3)
        self.assertEqual(self.controller.timeout, 30)
        self.assertEqual(self.controller.current_status, "idle")
        self.assertEqual(len(self.controller.execution_history), 0)
    
    def test_execute_sample_action(self):
        """Test executing a sample action."""
        action = {
            "type": "sample",
            "data": "test_data"
        }
        
        result = self.controller.execute_action(action)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("data", result)
        self.assertEqual(result["data"]["type"], "sample_response")
        self.assertEqual(result["data"]["original_data"], "test_data")
        self.assertEqual(len(self.controller.execution_history), 1)
    
    def test_execute_test_action(self):
        """Test executing a test action."""
        action = {"type": "test"}
        
        result = self.controller.execute_action(action)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["type"], "test_response")
        self.assertIn("controller_status", result["data"])
    
    def test_execute_status_action(self):
        """Test executing a status action."""
        action = {"type": "status"}
        
        result = self.controller.execute_action(action)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["name"], "TestController")
        self.assertEqual(result["data"]["current_status"], "idle")
    
    def test_execute_unknown_action(self):
        """Test executing an unknown action type."""
        action = {"type": "unknown_action"}
        
        result = self.controller.execute_action(action)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["type"], "unknown_action_response")
        self.assertIn("supported_types", result["data"])
    
    def test_execute_invalid_action(self):
        """Test executing an invalid action (missing type)."""
        action = {"data": "test"}
        
        result = self.controller.execute_action(action)
        
        self.assertEqual(result["status"], "error")
        self.assertIn("Invalid action format", result["error"])
    
    def test_validate_action_valid(self):
        """Test action validation with valid action."""
        action = {"type": "test", "data": "value"}
        
        is_valid = self.controller._validate_action(action)
        
        self.assertTrue(is_valid)
    
    def test_validate_action_invalid(self):
        """Test action validation with invalid action."""
        action = {"data": "value"}  # Missing type
        
        is_valid = self.controller._validate_action(action)
        
        self.assertFalse(is_valid)
    
    def test_get_status(self):
        """Test getting controller status."""
        status = self.controller.get_status()
        
        self.assertEqual(status["name"], "TestController")
        self.assertEqual(status["version"], "1.0.0")
        self.assertEqual(status["current_status"], "idle")
        self.assertEqual(status["execution_count"], 0)
        self.assertIsNone(status["last_execution"])
    
    def test_get_execution_history(self):
        """Test getting execution history."""
        # Execute an action first
        action = {"type": "test"}
        self.controller.execute_action(action)
        
        history = self.controller.get_execution_history()
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["action"], action)
        self.assertEqual(history[0]["status"], "success")
    
    def test_reset(self):
        """Test resetting controller state."""
        # Execute an action first
        action = {"type": "test"}
        self.controller.execute_action(action)
        
        # Verify state before reset
        self.assertEqual(len(self.controller.execution_history), 1)
        
        # Reset
        self.controller.reset()
        
        # Verify state after reset
        self.assertEqual(len(self.controller.execution_history), 0)
        self.assertEqual(self.controller.current_status, "idle")


if __name__ == '__main__':
    unittest.main()
