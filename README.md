# baseline-project-structure

A baseline Python project structure with controller, parser, and rollback components including Docker configuration and test files.

## Project Structure

```
baseline-project-structure/
├── .gitignore                      # Python .gitignore file
├── Dockerfile                      # Docker container configuration
├── docker-compose.yml              # Docker Compose configuration
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── config/
│   └── controller_config.json      # Application configuration
├── src/
│   ├── __init__.py                 # Package initialization
│   ├── main.py                     # Main application entry point
│   ├── controller/
│   │   ├── __init__.py
│   │   └── system_controller.py    # System controller implementation
│   ├── parser/
│   │   ├── __init__.py
│   │   └── action_parser.py        # Action parser implementation
│   └── rollback/
│       ├── __init__.py
│       └── rollback_manager.py     # Rollback manager implementation
└── tests/
    ├── test_controller.py          # Controller unit tests
    └── test_parser.py              # Parser unit tests
```

## Features

- **SystemController**: Manages system operations and coordinates between components
- **ActionParser**: Parses and validates input actions from multiple formats (JSON, YAML, XML)
- **RollbackManager**: Handles state management and rollback operations
- **Docker Support**: Ready-to-use Docker configuration for containerization
- **Configuration Management**: JSON-based configuration system
- **Comprehensive Testing**: Unit tests for core components
- **Logging**: Configurable logging system

## Quick Start

### Local Development

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd baseline-project-structure
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   cd src && python main.py
   ```

### Docker Development

1. Build the Docker image:
   ```bash
   docker build -t baseline-project .
   ```

2. Run with Docker Compose:
   ```bash
   docker-compose up
   ```

## Running Tests

Run unit tests using Python's unittest module:

```bash
# Run all tests
python -m unittest discover tests

# Run specific test files
python -m unittest tests.test_controller -v
python -m unittest tests.test_parser -v
```

## Configuration

The application uses a JSON configuration file located at `config/controller_config.json`. Key configuration sections:

- **controller**: System controller settings
- **parser**: Action parser configuration
- **rollback**: Rollback manager settings
- **logging**: Logging configuration

Example configuration:
```json
{
  "controller": {
    "name": "SystemController",
    "version": "1.0.0",
    "debug": false,
    "max_retries": 3,
    "timeout": 30
  },
  "parser": {
    "enabled": true,
    "strict_mode": false,
    "supported_formats": ["json", "yaml", "xml"]
  },
  "rollback": {
    "enabled": true,
    "max_history": 10,
    "auto_cleanup": true
  }
}
```

## Components

### SystemController

The main controller manages system operations and provides:
- Action execution with validation
- Execution history tracking
- Status monitoring
- Error handling and retry logic

### ActionParser

Handles input parsing and validation:
- Multiple format support (JSON, YAML, XML)
- Flexible input handling
- Schema validation
- Statistics tracking

### RollbackManager

Manages state changes and reversions:
- Checkpoint creation and management
- State rollback capabilities
- History management with configurable limits
- Import/export functionality

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is provided as-is for educational and development purposes.
