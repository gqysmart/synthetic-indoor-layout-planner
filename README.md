# Synthetic Indoor Layout Planner 🏠🤖

**AI Indoor Layout Planner** that combines **synthetic data generation**, **YOLO-based perception**, and **search-based planning** to automatically design furniture layouts in a room.  
Built as a course project, extended as a portfolio piece for synthetic data + computer vision.

---

## ✨ Features
- **Synthetic Data Factory** (Unity/Unreal)  
  - Generate room + furniture images with automatic labels (RGB, bbox, segmentation)  
- **Perception (YOLO + Depth)**  
  - Detect existing furniture objects  
  - Approximate 3D positions from 2D bounding boxes + depth/geometry priors  
- **Planning (CSP / A*)**  
  - Place new furniture while respecting constraints:  
    - No overlap  
    - No door/window blocking  
    - Maintain walkable paths  
- **Scoring System**  
  - Rule-based (movement flow, space usage)  
  - ML-based (detection confidence as proxy for realism)  
- **Demo (Unity/Unreal)**  
  - Visualize layouts and compare multiple solutions  

---

## 🏗 Tech Stack
- **Engine**: Unity or Unreal + [UnrealCV](https://unrealcv.org/) (for data generation & visualization)  
- **Computer Vision**: YOLOv5/YOLOv8 (PyTorch)  
- **Planning**: Python (A*, CSP, heuristics)  
- **Glue / Tools**: OpenCV, Numpy, Matplotlib  

---

## 📂 Repository Structure
synthetic-indoor-layout-planner/
├── engine/ # Unity/Unreal project for synthetic data & demo
├── perception/ # YOLO training, inference, depth estimation
├── planner/ # Planning algorithms (A*, CSP, scoring functions)
├── experiments/ # Data synthesis experiments (noise, data size curves)
├── docs/ # Report, notes, diagrams
└── README.md

---

## 🚀 Getting Started
### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/synthetic-indoor-layout-planner.git
cd synthetic-indoor-layout-planner
2. Install dependencies
pip install -r requirements.txt

3. Run YOLO detection
python perception/detect.py --source sample_room.jpg

4. Run the planner
PYTHONPATH=my-app uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

python planner/run_planner.py --input detected_objects.json

5. Visualize in Unity/Unreal

Import exported layout JSON → see the arrangement in 3D.

📊 Experiments

Data Size vs Accuracy: N ∈ {1k, 2k, 5k}

Noise vs Performance: σ ∈ {0, 10, 20}

Label Noise vs Robustness: flip rate ∈ {0%, 10%, 20%}

🎥 Demo

(Add GIF / screenshot later)
Example:

Input room photo

YOLO detection → recovered furniture

Planner generates 3 layouts → top-1 solution shown in Unity

📖 Course Alignment

Search & Planning → A* / CSP solver

Probability & Inference → noise experiments, uncertainty modeling

Supervised Learning → YOLO trained on synthetic data

Applications & Impact → AI-assisted interior design

🔮 Future Work

Multi-view reconstruction (SfM, COLMAP) for precise 3D geometry

RL for adaptive scoring weights

Larger synthetic dataset with domain randomization

Transfer learning to real apartment photos

👤 Author

Grant Ge (Qiyun Ge)

📧 Contact: Grantnj.ge@gmail.com

🌐 Portfolio: (link when ready)

💡 Focus: Synthetic Data · Computer Vision · AI Planning

---



## 📜 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
