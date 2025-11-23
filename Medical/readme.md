# 🏥 Multi-Agent Medical Report Analyzer

A sophisticated healthcare tool using multiple AI agents that collaborate to analyze medical reports from different expert perspectives.

## 🎯 Features

- **3 Specialized AI Agents:**
  - 🔴 **Dr. Diagnostic** - Primary physician for initial analysis
  - 🔵 **Dr. Specialist** - Expert providing detailed medical insights
  - 🟢 **Dr. Coordinator** - Synthesizing findings into actionable plans

- **Multiple Input Methods:**
  - ✍️ Type or paste text directly
  - 📸 Upload images with OCR (automatically extract text from medical documents)
  - 📋 Load pre-configured sample cases

- **Real-time Logging** - Watch agents collaborate in real-time
- **Comprehensive Reports** - Download complete analysis as text file
- **Sample Medical Cases** - Test immediately with realistic scenarios

## 📦 Installation

### 1. Install Tesseract OCR (for image text extraction)

**Windows:**
```bash
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
# Run the installer and add to PATH
```

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Get your Groq API key:
   - Visit: https://console.groq.com/keys
   - Create a free account
   - Generate an API key

3. Add your API key to `.env`:
```bash
GROQ_API_KEY=gsk_your_actual_api_key_here
```

## 🚀 Usage

1. **Start the application:**
```bash
streamlit run app.py
```

2. **Choose input method:**
   - Type/paste medical report text
   - Upload an image of a medical document (OCR will extract text)
   - Select a sample case to try

3. **Click "Analyze"** and watch the agents collaborate!

4. **Review results** from each agent in separate tabs

5. **Download** the complete report if needed

## 📁 Project Structure

```
medical-agent-analyzer/
├── app.py                 # Main Streamlit UI
├── agents.py              # Multi-agent system logic
├── .env                   # Environment variables (create this)
├── .env.example           # Template for environment variables
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔧 Troubleshooting

### OCR not working?
- Ensure Tesseract is installed and in your PATH
- Test: `tesseract --version` in terminal
- Windows: Add Tesseract install directory to system PATH

### API Key errors?
- Verify `.env` file exists in project root
- Check API key is valid at https://console.groq.com/keys
- Ensure no extra spaces or quotes in `.env` file

### Import errors?
```bash
pip install --upgrade -r requirements.txt
```

## ⚠️ Disclaimer

This is a demonstration tool for educational purposes. **Always consult qualified healthcare professionals** for medical advice. This tool should not be used as a substitute for professional medical diagnosis or treatment.

## 🛠️ Tech Stack

- **Streamlit** - Web interface
- **Agno** - Agent orchestration framework
- **Groq** - Fast LLM inference (Llama 3.3 70B)
- **Pytesseract** - OCR for image text extraction
- **Python-dotenv** - Environment variable management

## 📝 Example Use Cases

1. **Emergency Department** - Quick multi-perspective analysis of incoming cases
2. **Medical Education** - Demonstrate differential diagnosis approaches
3. **Second Opinions** - Get multiple expert viewpoints on complex cases
4. **Research** - Analyze patterns across multiple medical reports

## 🤝 Contributing

Feel free to open issues or submit pull requests for improvements!

## 📄 License

MIT License - feel free to use and modify as needed.
