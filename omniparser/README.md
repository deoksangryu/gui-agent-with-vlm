# OmniParser: Screen Parsing tool for Pure Vision Based GUI Agent

OmniParser is a comprehensive method for parsing user interface screenshots into structured and easy-to-understand elements, which significantly enhances the ability of GPT-4V to generate actions that can be accurately grounded in the corresponding regions of the interface.

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Usage

1. **Demo Script**
```bash
python omniparser_demo.py
```

2. **Gradio Demo**
```bash
python gradio_demo.py
```

3. **Jupyter Notebook**
```bash
jupyter notebook demo.ipynb
```

## Features

- **Pure Vision-based**: Uses only visual information without text-based approaches
- **Precise Element Detection**: Accurate location identification of icons, buttons, text, and other UI elements
- **Interaction Possibility Prediction**: Determines whether each screen element is interactable
- **Multi-model Support**: YOLO-based detection model and BLIP2/Florence2 caption model

## Technology Stack

- **Object Detection**: YOLO (Ultralytics)
- **Image Captioning**: BLIP2, Florence2
- **OCR**: EasyOCR, PaddleOCR
- **Framework**: PyTorch, Transformers
- **Web Interface**: Gradio

## Core Features

1. **Icon Detection**: Accurate bounding box generation for UI elements using YOLO model
2. **Functional Description**: Natural language description of each UI element's function and purpose
3. **OCR Integration**: Accurate recognition and location of text elements
4. **Interaction Analysis**: Distinguishes between clickable elements and information display elements

## Achievements

- **Screen Spot Pro benchmark** new SOTA performance achievement (39.5%)
- **Windows Agent Arena** best performance achievement
- #1 trending model on Hugging Face model hub
- Developed and supported by Microsoft Research

## Citation

```bibtex
@misc{lu2024omniparserpurevisionbased,
      title={OmniParser for Pure Vision Based GUI Agent}, 
      author={Yadong Lu and Jianwei Yang and Yelong Shen and Ahmed Awadallah},
      year={2024},
      eprint={2408.00203},
      archivePrefix={arXiv},
      primaryClass={cs.CV}
}
```
