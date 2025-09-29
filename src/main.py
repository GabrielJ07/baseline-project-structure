#!/usr/bin/env python3
"""
Main entry point for the baseline project.
"""

import logging
import sys
import json
from pathlib import Path

from controller.system_controller import SystemController
from parser.action_parser import ActionParser
from rollback.rollback_manager import RollbackManager


def setup_logging(config: dict) -> None:
    """Setup logging configuration."""
    log_config = config.get("logging", {})
    level = getattr(logging, log_config.get("level", "INFO"))
    format_str = log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Create logs directory if specified
    log_file = log_config.get("file")
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=level,
            format=format_str,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
    else:
        logging.basicConfig(level=level, format=format_str)


def load_config(config_path: str = "config/controller_config.json") -> dict:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in configuration file: {e}")
        return {}


def main():
    """Main application entry point."""
    # Load configuration
    config = load_config()
    
    # Setup logging
    setup_logging(config)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting baseline project application")
    
    try:
        # Initialize components
        controller = SystemController(config.get("controller", {}))
        parser = ActionParser(config.get("parser", {}))
        rollback_manager = RollbackManager(config.get("rollback", {}))
        
        logger.info("All components initialized successfully")
        
        # Example usage - this would be replaced with actual application logic
        logger.info("Application is running...")
        
        # Simulate some work
        sample_action = {"type": "sample", "data": "test"}
        parsed_action = parser.parse(sample_action)
        logger.info(f"Parsed action: {parsed_action}")
        
        # Execute action through controller
        result = controller.execute_action(parsed_action)
        logger.info(f"Action execution result: {result}")
        
        logger.info("Application completed successfully")
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()