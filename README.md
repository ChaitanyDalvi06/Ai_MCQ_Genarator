<div align="center">

# 🎓 AI MCQ Generator

### Transform your study materials into practice questions instantly

*An AI-powered tool that generates multiple-choice questions from PDFs or text using local AI*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-black.svg)](https://ollama.ai)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Features](#-features) • [Quick Start](#-quick-start) • [Usage](#-usage) • [Configuration](#-configuration)

---

</div>

## ✨ Features

<table>
<tr>
<td>

🤖 **Local AI Powered**  
No internet needed - runs 100% on your machine

📄 **PDF Support**  
Upload PDFs and extract text instantly

</td>
<td>

🎯 **Customizable**  
Choose difficulty & question count (1-20)

💡 **Smart Explanations**  
Get detailed answers for every question

</td>
<td>

✨ **Beautiful UI**  
Clean, ChatGPT-like interface

🚀 **Lightning Fast**  
Generate questions in seconds

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Ollama** ([Install Guide](https://ollama.ai))

### Installation

**1️⃣ Install & Start Ollama**

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Pull the AI model (recommended: ~2GB)
ollama pull llama3.2

# Start Ollama server
ollama serve
```

> 💡 Keep this terminal open - Ollama needs to run in the background

**2️⃣ Setup Backend**

```bash
# Navigate to backend folder
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000
```

**3️⃣ Launch Frontend**

```bash
# Open in your browser
open frontend/index.html

# Or simply drag frontend/index.html into your browser
```

---

## 🎯 Usage

<div align="center">

### Three Simple Steps

```mermaid
graph LR
    A[📄 Upload PDF] --> B[⚙️ Configure]
    B --> C[✨ Generate MCQs]
    style A fill:#4CAF50
    style B fill:#2196F3
    style C fill:#FF9800
```

</div>

1. **Upload Your Material**
   - Click "Upload PDF" or paste text directly
   
2. **Customize Settings**
   - Questions: 1-20
   - Difficulty: Easy / Medium / Hard

3. **Generate & Practice**
   - Click "Generate MCQs"
   - Answer questions interactively
   - Review explanations

---

## 🛠️ Configuration

### Change AI Model

```python
# backend/main.py (line ~46)
OLLAMA_MODEL = "llama3.2"  # Try: mistral, gemma, phi3
```

### Adjust Creativity

```python
# backend/main.py (line ~47)
OLLAMA_TEMPERATURE = 0.3  # 0.0 = Focused, 1.0 = Creative
```

### Modify Backend URL

```javascript
// frontend/index.html (line ~269)
const API_BASE_URL = 'http://localhost:8000';
```

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Vanilla JS, HTML5, CSS3 |
| **Backend** | FastAPI (Python) |
| **AI Engine** | Ollama (Local LLM) |
| **PDF Processing** | pdfplumber, PyPDF2 |

---

## 📁 Project Structure

```
AI-MCQ-Generator/
│
├── 📁 frontend/
│   └── index.html          # Complete UI (HTML + CSS + JS)
│
├── 📁 backend/
│   ├── main.py            # FastAPI server
│   └── requirements.txt   # Python packages
│
└── README.md              # You are here!
```

---

## 🐛 Troubleshooting

<details>
<summary><b>Cannot connect to Ollama</b></summary>

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```
</details>

<details>
<summary><b>Model not found error</b></summary>

```bash
# Pull the model first
ollama pull llama3.2

# Verify it's installed
ollama list
```
</details>

<details>
<summary><b>PDF text extraction fails</b></summary>

- Ensure PDF is text-based (not scanned images)
- Try a different PDF file
- Check if PDF is password-protected
</details>

<details>
<summary><b>Slow generation speed</b></summary>

- Use smaller models: `phi3` or `llama3.2`
- Reduce number of questions
- Increase chunk size in `main.py`
</details>

---


📖 **Interactive Docs:** Visit `http://localhost:8000/docs` after starting the server

---

## 💡 Performance Tips

- ⚡ **Faster Models**: Use `llama3.2` or `phi3` for speed
- 🎯 **Lower Temperature**: Set 0.2-0.4 for consistent results
- 📦 **Smaller Batches**: Generate 5-10 questions at a time
- 🔄 **Keep Ollama Running**: First generation loads model (slower), subsequent ones are fast


---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

<div align="center">

### 🌟 Star this repo if you find it useful!

Made with ❤️ for learners 

**[Report Bug](https://github.com/yourusername/ai-mcq-generator/issues)** • **[Request Feature](https://github.com/yourusername/ai-mcq-generator/issues)**

</div>
