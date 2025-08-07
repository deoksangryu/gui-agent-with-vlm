# UI Test Framework

A comprehensive testing framework for GUI Agent applications with vision-language models.

## Overview

This framework provides tools and utilities for testing GUI Agent applications, including screenshot analysis, UI element detection, and automated testing capabilities.

## Features

- **Screenshot Analysis**: Automated screenshot capture and analysis
- **UI Element Detection**: Detection and validation of UI elements
- **Automated Testing**: End-to-end testing capabilities
- **Performance Monitoring**: Real-time performance metrics
- **Debug Tools**: Comprehensive debugging and logging

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Usage

1. **Basic Testing**
```bash
python coordinate_checker.py
```

2. **Screenshot Analysis**
```bash
python click_server.py
```

3. **Performance Testing**
```bash
python performance_test.py
```

## Project Structure

```
ui-test-framework/
├── tests/                    # Test cases and scenarios
├── utils/                    # Utility functions
├── examples/                 # Example implementations
├── results/                  # Test results and outputs
└── docs/                     # Documentation
```

## Components

### Coordinate Checker
Validates coordinate accuracy and precision for UI interactions.

### Click Server
Handles automated clicking and interaction testing.

### Performance Monitor
Tracks and analyzes performance metrics.

## Testing Capabilities

- **UI Element Detection**: Test accuracy of UI element identification
- **Coordinate Validation**: Verify click coordinate precision
- **Performance Benchmarking**: Measure response times and throughput
- **Regression Testing**: Automated regression test suites
- **Integration Testing**: End-to-end workflow testing

## Configuration

The framework can be configured through environment variables or configuration files:

```bash
export UI_TEST_DEBUG=true
export UI_TEST_TIMEOUT=30
export UI_TEST_SCREENSHOT_DIR=./screenshots
```

## Results

Test results are stored in the `results/` directory with detailed logs and performance metrics.

## Contributing

Please read our contributing guidelines before submitting pull requests.

## License

This project is licensed under the MIT License. 