# ShowUI

Open-source, End-to-end, Lightweight, Vision-Language-Action model for GUI Agent & Computer Use.

ShowUI 是一款开源的、端到端、轻量级的视觉-语言-动作模型，专为 GUI 智能体设计。

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Usage

1. **Gradio Demo**
```bash
python app.py
```

2. **API Service**
```bash
python api.py
```

3. **vLLM Inference**
```python
# See inference_vllm.ipynb for details
```

## Features

- **Vision-Language-Action Model**: Analyzes screenshots to understand GUI elements
- **Lightweight Design**: 2B parameters for efficient inference
- **Multi-Model Support**: Qwen2VL, Qwen2.5VL compatibility
- **Real-time Inference**: High-speed inference with vLLM
- **API Service**: Web interface through Gradio

## Model Training

See [TRAIN.md](TRAIN.md) for detailed training instructions.

## Citation

```bibtex
@misc{lin2024showui,
      title={ShowUI: One Vision-Language-Action Model for GUI Visual Agent}, 
      author={Kevin Qinghong Lin and Linjie Li and Difei Gao and Zhengyuan Yang and Shiwei Wu and Zechen Bai and Weixian Lei and Lijuan Wang and Mike Zheng Shou},
      year={2024},
      eprint={2411.17465},
      archivePrefix={arXiv},
      primaryClass={cs.CV}
}
```
