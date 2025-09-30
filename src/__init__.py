"""
Baseline project package initialization.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main modules for easy access
from .controller.system_controller import SystemController
from .parser.action_parser import ActionParser
from .rollback.rollback_manager import RollbackManager

__all__ = [
    "SystemController",
    "ActionParser", 
    "RollbackManager"
]