"""
Unit tests for ActionParser.
"""

import unittest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parser.action_parser import ActionParser


class TestActionParser(unittest.TestCase):
    """Test cases for ActionParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "enabled": True,
            "strict_mode": False,
            "supported_formats": ["json", "yaml", "xml"]
        }
        self.parser = ActionParser(self.config)
    
    def test_initialization(self):
        """Test parser initialization."""
        self.assertTrue(self.parser.enabled)
        self.assertFalse(self.parser.strict_mode)
        self.assertEqual(self.parser.supported_formats, ["json", "yaml", "xml"])
        self.assertEqual(self.parser.parse_count, 0)
        self.assertEqual(self.parser.error_count, 0)
    
    def test_parse_dict_input(self):
        """Test parsing dictionary input."""
        input_data = {"type": "test", "data": "value"}
        
        result = self.parser.parse(input_data)
        
        self.assertEqual(result["type"], "test")
        self.assertEqual(result["data"], "value")
        self.assertIn("timestamp", result)
        self.assertIn("id", result)
    
    def test_parse_json_string(self):
        """Test parsing JSON string input."""
        input_data = '{"type": "json_test", "data": "json_value"}'
        
        result = self.parser.parse(input_data)
        
        self.assertEqual(result["type"], "json_test")
        self.assertEqual(result["data"], "json_value")
        self.assertEqual(self.parser.format_stats["json"], 1)
    
    def test_parse_plain_text(self):
        """Test parsing plain text input."""
        input_data = "This is just plain text"
        
        result = self.parser.parse(input_data)
        
        self.assertEqual(result["type"], "text")
        self.assertEqual(result["data"], "This is just plain text")
    
    def test_parse_other_input_types(self):
        """Test parsing non-string, non-dict input types."""
        input_data = 12345
        
        result = self.parser.parse(input_data)
        
        self.assertEqual(result["type"], "raw")
        self.assertEqual(result["data"], 12345)
        self.assertEqual(result["data_type"], "int")
    
    def test_parse_disabled(self):
        """Test parsing when parser is disabled."""
        self.parser.enabled = False
        input_data = {"type": "test"}
        
        result = self.parser.parse(input_data)
        
        self.assertEqual(result["type"], "disabled")
        self.assertEqual(result["data"], input_data)
    
    def test_validate_and_normalize_action(self):
        """Test action validation and normalization."""
        action = {"data": "value"}  # Missing type
        
        result = self.parser._validate_and_normalize_action(action)
        
        self.assertEqual(result["type"], "unknown")  # Should add default type
        self.assertIn("timestamp", result)
        self.assertIn("id", result)
    
    def test_is_valid_action_type(self):
        """Test action type validation."""
        valid_types = ["sample", "test", "status", "create", "update"]
        invalid_types = ["invalid", "bad_type"]
        
        for action_type in valid_types:
            self.assertTrue(self.parser._is_valid_action_type(action_type))
        
        for action_type in invalid_types:
            self.assertFalse(self.parser._is_valid_action_type(action_type))
    
    def test_get_statistics(self):
        """Test getting parser statistics."""
        # Parse some data to generate statistics
        self.parser.parse({"type": "test1"})
        self.parser.parse('{"type": "test2"}')  # JSON
        
        stats = self.parser.get_statistics()
        
        self.assertEqual(stats["total_parsed"], 2)
        self.assertEqual(stats["errors"], 0)
        self.assertEqual(stats["success_rate"], 100.0)
        self.assertEqual(stats["format_breakdown"]["json"], 1)
    
    def test_reset_statistics(self):
        """Test resetting parser statistics."""
        # Parse some data first
        self.parser.parse({"type": "test"})
        self.parser.parse('{"type": "test"}')
        
        # Verify statistics before reset
        self.assertEqual(self.parser.parse_count, 2)
        
        # Reset statistics
        self.parser.reset_statistics()
        
        # Verify statistics after reset
        self.assertEqual(self.parser.parse_count, 0)
        self.assertEqual(self.parser.error_count, 0)
        self.assertEqual(self.parser.format_stats["json"], 0)


if __name__ == '__main__':
    unittest.main()
