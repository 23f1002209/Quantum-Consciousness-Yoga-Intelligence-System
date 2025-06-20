# QCYIS: Quantum Consciousness Yoga Intelligence System 🧘‍♂️🤖

> **An AI-powered yoga assistant for real-time pose correction, consciousness monitoring, and intelligent guidance—all running locally.**

---

## Overview

QCYIS is a yoga assistant that integrates computer vision, consciousness analytics, and local LLM-powered chat—all in a seamless, interactive web application.  
**All data stays on your device. No cloud. No compromise.**

---

## Key Features

- **Real-Time Pose Detection & Correction:**  
  Uses MediaPipe to analyze your yoga posture, overlaying 33-point landmarks and providing instant, actionable feedback on your alignment and form.

- **AI Yoga Assistant (Local LLM):**  
  Ask questions, get pose instructions, breathing exercises, or meditation guidance—all powered by Llama 3.1 via Ollama, running entirely on your machine.

- **Consciousness Metrics Dashboard:**  
  Simulated PCI (Perturbational Complexity Index), meditation depth, and coherence scores update live as you practice.

- **Biofield & Chakra Visualization:**  
  See your energetic state visualized with animated chakra indicators and real-time balance feedback.

- **Quantum Processing Simulation:**  
  Quantum metrics (qubit coherence, entanglement strength, processing power) offer a futuristic, engaging view of your mind-body state.

- **Complete Privacy:**  
  No data leaves your device. Camera frames, chat, and analytics are processed locally.

---

## Application Interface

| Feature Area           | What You See/Do                                                                                       |
|------------------------|------------------------------------------------------------------------------------------------------|
| **Header**             | Animated "QCYIS" title, live connection status indicator                                             |
| **Live Video Feed**    | Webcam stream with pose landmark overlay, pose name, and quality score                               |
| **Pose Corrections**   | Real-time, actionable suggestions for improving your alignment, plus safety tips                     |
| **Consciousness Panel**| PCI score, meditation depth, coherence, and animated progress bars                                   |
| **Chakra Visualization** | 7 glowing chakra indicators, each reflecting simulated activation and balance                      |
| **Quantum Metrics**    | Qubit coherence, entanglement, and processing power, all updating live                               |
| **Chatbot**            | Ask anything about yoga, breathwork, or meditation—get context-aware, safe, and private guidance     |

---



### Prerequisites

- Python 3.8+
- Webcam
- Modern browser (Chrome, Firefox, Edge, Safari)
- [Ollama](https://ollama.com/) installed locally (`ollama serve`)
- Llama 3.1 model pulled (`ollama pull llama3.1`)

### Setup

```bash
cd qcyis-project
python -m venv .venv
# Activate your virtual environment:
# On Windows:
.venv/Scripts/activate
# On macOS/Linux:
source .venv/bin/activate
# Install dependencies
pip install -r backend/requirements.txt
pip install -r mcp-server/requirements.txt
```

### Running

```bash
# Start backend
python -m backend.app.main
# Start MCP server
python mcp-server/server.py
# Start frontend
cd frontend
python -m http.server 3000
```

Open your browser to [http://localhost:3000](http://localhost:3000).

---

## Usage

1. **Start Camera:** Click "Start Camera" and allow permissions.
2. **Start Pose Detection:** Click "Start Pose Detection" to see live feedback.
3. **Read Corrections:** Adjust your posture based on real-time suggestions.
4. **Monitor Consciousness:** Watch your PCI, coherence, and chakra balance update live.
5. **Chat with the AI:** Ask for pose help, breathing instructions, or meditation prompts.
6. **All data stays local:** Nothing leaves your device at any time.

---

## Project Structure

```
qcyis-project/
├── backend/         # FastAPI backend and AI services
├── frontend/        # HTML/CSS/JS client
├── mcp-server/      # Yoga tools and routines
├── scripts/         # Setup and run scripts
└── README.md
```

---

## Extensibility

- **Add more poses:** Expand the pose reference set in the backend.
- **Custom chat tools:** Integrate new yoga routines, breathing guides, or mindfulness modules via the MCP server.
- **UI themes:** Easily adapt the CSS for different visual styles.

---

## Credits

- [MediaPipe](https://mediapipe.dev/)
- [Ollama](https://ollama.com/)
- [Llama 3.1](https://ollama.com/library/llama3)
- [FastAPI](https://fastapi.tiangolo.com/)

---

## License

MIT License

---

## Acknowledgements

This project was inspired by the intersection of yoga, wellness, and responsible AI.  
*Built with privacy and empowerment in mind.*

---

> **QCYIS — Where ancient wisdom meets quantum intelligence.**

---

*For questions, suggestions, or contributions, please open an issue or pull request!*
