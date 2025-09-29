"""
Action Parser for parsing and validating input actions.
"""

import json
import logging
import yaml
import xml.etree.ElementTree as ET
from typing import Dict, Any, Union, List
from datetime import datetime


class ActionParser:
    """
    Parser class for handling different input formats and converting them
    to standardized action objects.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the ActionParser.
        
        Args:
            config: Configuration dictionary for the parser
        """
        self.config = config
        self.enabled = config.get("enabled", True)
        self.strict_mode = config.get("strict_mode", False)
        self.supported_formats = config.get("supported_formats", ["json", "yaml", "xml"])
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Initialized ActionParser with formats: {self.supported_formats}")
        
        # Track parsing statistics
        self.parse_count = 0
        self.error_count = 0
        self.format_stats = {fmt: 0 for fmt in self.supported_formats}
    
    def parse(self, input_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse input data into a standardized action format.
        
        Args:
            input_data: Raw input data (string or dict)
            
        Returns:
            Parsed action dictionary
        """
        if not self.enabled:
            self.logger.warning("Parser is disabled")
            return {"type": "disabled", "data": input_data}
        
        self.parse_count += 1
        
        try:
            # If already a dict, validate and return
            if isinstance(input_data, dict):
                return self._validate_and_normalize_action(input_data)
            
            # If string, try to detect format and parse
            if isinstance(input_data, str):
                return self._parse_string_input(input_data)
            
            # Handle other types
            return self._parse_other_input(input_data)
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Parsing failed: {e}")
            
            if self.strict_mode:
                raise
            
            return {
                "type": "parse_error",
                "error": str(e),
                "original_input": str(input_data),
                "timestamp": datetime.now().isoformat()
            }
    
    def _parse_string_input(self, input_str: str) -> Dict[str, Any]:
        """
        Parse string input by detecting format.
        
        Args:
            input_str: String input to parse
            
        Returns:
            Parsed action dictionary
        """
        input_str = input_str.strip()
        
        # Try JSON first
        if "json" in self.supported_formats:
            try:
                data = json.loads(input_str)
                self.format_stats["json"] += 1
                return self._validate_and_normalize_action(data)
            except json.JSONDecodeError:
                pass
        
        # Try YAML
        if "yaml" in self.supported_formats:
            try:
                data = yaml.safe_load(input_str)
                if isinstance(data, dict):
                    self.format_stats["yaml"] += 1
                    return self._validate_and_normalize_action(data)
            except yaml.YAMLError:
                pass
        
        # Try XML
        if "xml" in self.supported_formats:
            try:
                root = ET.fromstring(input_str)
                data = self._xml_to_dict(root)
                self.format_stats["xml"] += 1
                return self._validate_and_normalize_action(data)
            except ET.ParseError:
                pass
        
        # If no format worked, treat as plain text
        return {
            "type": "text",
            "data": input_str,
            "timestamp": datetime.now().isoformat()
        }
    
    def _parse_other_input(self, input_data: Any) -> Dict[str, Any]:
        """
        Handle non-string, non-dict input types.
        
        Args:
            input_data: Input data of unknown type
            
        Returns:
            Parsed action dictionary
        """
        return {
            "type": "raw",
            "data": input_data,
            "data_type": type(input_data).__name__,
            "timestamp": datetime.now().isoformat()
        }
    
    def _validate_and_normalize_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize an action dictionary.
        
        Args:
            action: Action dictionary to validate
            
        Returns:
            Validated and normalized action dictionary
        """
        # Ensure required fields
        if "type" not in action:
            action["type"] = "unknown"
        
        # Add metadata if not present
        if "timestamp" not in action:
            action["timestamp"] = datetime.now().isoformat()
        
        if "id" not in action:
            action["id"] = f"action_{self.parse_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Validate action type
        if self.strict_mode and not self._is_valid_action_type(action["type"]):
            raise ValueError(f"Invalid action type: {action['type']}")
        
        return action
    
    def _is_valid_action_type(self, action_type: str) -> bool:
        """
        Check if action type is valid.
        
        Args:
            action_type: Action type to validate
            
        Returns:
            True if valid, False otherwise
        """
        valid_types = [
            "sample", "test", "status", "create", "update", "delete",
            "query", "command", "notification", "text", "raw", "unknown"
        ]
        return action_type in valid_types
    
    def _xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """
        Convert XML element to dictionary.
        
        Args:
            element: XML element to convert
            
        Returns:
            Dictionary representation of XML
        """
        result = {}
        
        # Add attributes
        if element.attrib:
            result.update(element.attrib)
        
        # Handle text content
        if element.text and element.text.strip():
            if result:
                result['_text'] = element.text.strip()
            else:
                return element.text.strip()
        
        # Handle child elements
        for child in element:
            child_data = self._xml_to_dict(child)
            
            if child.tag in result:
                # Convert to list if multiple elements with same tag
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        # Use root tag as type if no type specified
        if not result.get("type"):  
            result["type"] = element.tag
        
        return result
    
    def validate_schema(self, action: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        Validate action against a schema.
        
        Args:
            action: Action dictionary to validate
            schema: Schema dictionary for validation
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic schema validation (can be extended with jsonschema library)
            required_fields = schema.get("required", [])
            
            for field in required_fields:
                if field not in action:
                    self.logger.error(f"Missing required field: {field}")
                    return False
            
            # Type validation
            field_types = schema.get("types", {})
            for field, expected_type in field_types.items():
                if field in action:
                    actual_type = type(action[field]).__name__
                    if actual_type != expected_type:
                        self.logger.error(f"Field {field} has type {actual_type}, expected {expected_type}")
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Schema validation error: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get parsing statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            "total_parsed": self.parse_count,
            "errors": self.error_count,
            "success_rate": (self.parse_count - self.error_count) / max(self.parse_count, 1) * 100,
            "format_breakdown": self.format_stats.copy(),
            "config": self.config
        }
    
    def reset_statistics(self) -> None:
        """Reset parsing statistics."""
        self.parse_count = 0
        self.error_count = 0
        self.format_stats = {fmt: 0 for fmt in self.supported_formats}
        self.logger.info("Parser statistics reset")