# GUI Agent with VLM - Project Integration Summary

## Overview

This repository integrates multiple AI GUI Agent projects into a comprehensive portfolio showcasing vision-language models for computer automation and UI interaction.

## Integrated Projects

### 1. ShowUI
**Location**: `showui/`
- **Type**: Vision-Language-Action Model
- **Purpose**: GUI element recognition and action generation
- **Key Features**:
  - 2B parameter lightweight model
  - Real-time inference with vLLM
  - Multi-model support (Qwen2VL, Qwen2.5VL)
  - API service and Gradio interface
- **Achievements**: CVPR 2025 acceptance, NeurIPS 2024 outstanding paper award

### 2. OmniParser v2 (Complete Implementation)
**Location**: `omniparser/`
- **Type**: Screen Parsing Tool
- **Purpose**: Pure vision-based UI element detection and description
- **Key Features**:
  - YOLO-based icon detection
  - BLIP2/Florence2 caption models
  - OCR integration (EasyOCR, PaddleOCR)
  - Interaction possibility prediction
  - Step-by-step demo scripts
  - OmniTool integration for Windows VM control
- **Components**:
  - `util/`: Core utility functions (utils.py, box_annotator.py, omniparser.py)
  - `steps/`: Step-by-step demo scripts for different use cases
  - `omnitool/`: Windows VM control integration
  - `eval/`: Evaluation scripts and benchmarks
  - `docs/`: Documentation and guides
- **Achievements**: Screen Spot Pro benchmark SOTA (39.5%), #1 trending on Hugging Face

### 3. Angular Chatbot Application
**Location**: `angular-chatbot/`
- **Type**: Frontend Web Application
- **Purpose**: User interface for AI chatbot interactions
- **Key Features**:
  - Modern Angular 18 framework
  - Real-time chat interface
  - Screenshot integration
  - Responsive design
  - Component-based architecture

### 4. UI Test Framework
**Location**: `ui-test-framework/`
- **Type**: Testing and Development Tools
- **Purpose**: Comprehensive testing framework for GUI Agent applications
- **Key Features**:
  - Automated screenshot analysis
  - UI element detection testing
  - Performance monitoring
  - Debug tools and logging

## Technical Stack

### Backend Technologies
- **Python 3.8+**: Core programming language
- **PyTorch 2.0+**: Deep learning framework
- **Transformers**: Hugging Face model library
- **vLLM**: High-speed inference engine
- **Gradio**: Web interface framework
- **FastAPI**: API development framework

### Frontend Technologies
- **Angular 18**: Modern frontend framework
- **TypeScript**: Type-safe JavaScript
- **CSS3**: Modern styling
- **RxJS**: Reactive programming

### AI/ML Models
- **Qwen2VL/Qwen2.5VL**: Vision-language models
- **YOLO (Ultralytics)**: Object detection
- **BLIP2/Florence2**: Image captioning
- **EasyOCR/PaddleOCR**: Text recognition

## Project Structure

```
gui-agent-with-vlm/
├── showui/                    # ShowUI Vision-Language-Action model
│   ├── model/                 # Model implementations
│   ├── data/                  # Data processing
│   ├── training/              # Training scripts
│   ├── inference/             # Inference and API
│   └── docs/                  # Documentation
├── omniparser/                # OmniParser v2 screen parsing (Complete)
│   ├── util/                  # Core utility functions
│   │   ├── utils.py          # Main utility functions
│   │   ├── box_annotator.py  # Bounding box annotation
│   │   └── omniparser.py     # OmniParser core
│   ├── steps/                 # Step-by-step demos
│   │   ├── step1_basic_demo.py
│   │   ├── step2_toss_initial_attempt.py
│   │   ├── step3_korean_ocr_support.py
│   │   ├── step4_improved_ocr_sensitivity.py
│   │   ├── step5_blip2_model_switch.py
│   │   └── step6_final_summary.py
│   ├── omnitool/             # Windows VM control
│   │   ├── gradio/           # Gradio interface
│   │   ├── omnibox/          # VM management
│   │   └── omniparserserver/ # Server components
│   ├── eval/                 # Evaluation scripts
│   ├── docs/                 # Documentation
│   ├── imgs/                 # Example images
│   ├── omniparser_demo.py    # Main demo script
│   └── gradio_demo.py        # Gradio demo
├── angular-chatbot/           # Angular chatbot application
│   ├── src/                   # Source code
│   ├── components/            # Angular components
│   └── services/              # Services
├── ui-test-framework/         # UI testing framework
│   ├── tests/                 # Test cases
│   └── examples/              # Example implementations
├── requirements.txt           # Python dependencies
├── README.md                  # Main project documentation
└── .gitignore                 # Git ignore rules
```

## Key Achievements

### Academic Recognition
- **CVPR 2025**: ShowUI paper acceptance
- **NeurIPS 2024**: Outstanding paper award for ShowUI
- **Screen Spot Pro**: SOTA performance (39.5%) with OmniParser v2
- **Windows Agent Arena**: Best performance achievement

### Technical Innovation
- **Pure Vision-based UI Parsing**: OmniParser's innovative approach
- **Lightweight VLA Model**: ShowUI's efficient 2B parameter design
- **Multi-model Integration**: Support for various latest models
- **Real-time Processing**: High-speed inference capabilities
- **Complete Implementation**: Full OmniParser v2 codebase with 93 files

### Community Impact
- **Hugging Face #1 Trending**: OmniParser model popularity
- **Open Source Contribution**: Active community participation
- **Dataset Publication**: ShowUI-desktop, ShowUI-web datasets
- **Model Deployment**: Public model sharing

## Development Workflow

### 1. Model Development
- **ShowUI**: Vision-language-action model training and fine-tuning
- **OmniParser**: Object detection and caption model integration
- **Performance Optimization**: vLLM, quantization, batch processing

### 2. Application Development
- **Angular Frontend**: Modern web interface development
- **API Integration**: RESTful API services
- **Testing Framework**: Comprehensive testing suite

### 3. Deployment and Distribution
- **Hugging Face**: Model and dataset hosting
- **Gradio Spaces**: Interactive demos
- **Local Execution**: OOTB deployment support

## Future Roadmap

### Short-term Goals
- **Multi-agent Orchestration**: Enhanced agent collaboration
- **UI/UX Improvements**: Better user experience
- **Domain Specialization**: Field-specific agent development

### Long-term Vision
- **Real-time Processing**: Faster inference optimization
- **Multi-platform Support**: Cross-platform compatibility
- **Custom Training**: User-defined model training
- **Enterprise Integration**: Business application deployment

## Getting Started

### Prerequisites
- Python 3.8+
- PyTorch 2.0+
- Node.js (for Angular app)
- CUDA (for GPU acceleration)

### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd gui-agent-with-vlm

# Install Python dependencies
pip install -r requirements.txt

# Install Angular dependencies
cd angular-chatbot
npm install

# Run ShowUI demo
cd ../showui
python app.py

# Run OmniParser demo
cd ../omniparser
python omniparser_demo.py

# Run Angular app
cd ../angular-chatbot
ng serve
```

## Contributing

We welcome contributions! Please see our contributing guidelines for details on:
- Code style and standards
- Testing requirements
- Documentation updates
- Issue reporting

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions and support:
- GitHub Issues: Technical questions and bug reports
- Documentation: Comprehensive project documentation
- Community: Active development community

---

**Last Updated**: 2024  
**Version**: 1.0.0  
**Maintainers**: AI GUI Agent Development Team 