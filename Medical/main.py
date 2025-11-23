import streamlit as st
from datetime import datetime
import os
from pathlib import Path
from PIL import Image
import io
import re

# Install required packages:
# pip install streamlit agno groq python-dotenv pytesseract pillow

try:
    from dotenv import load_dotenv
    import pytesseract
    from agents import MedicalAgentSystem
except Exception as e:
    import traceback
    st.error(f"Import error: {str(e)}")
    # Show full traceback in the app to help diagnose which import failed
    st.text(traceback.format_exc())
    st.stop()

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(page_title="Multi-Agent Medical Analyzer", page_icon="🏥", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .agent-card {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid;
    }
    .diagnostic { border-left-color: #FF6B6B; background-color: #FFF5F5; }
    .specialist { border-left-color: #4ECDC4; background-color: #F0FFFE; }
    .coordinator { border-left-color: #95E1D3; background-color: #F5FFFD; }
    .log-entry { 
        font-size: 12px; 
        color: #666; 
        padding: 5px; 
        margin: 2px 0;
        border-left: 2px solid #ddd;
        padding-left: 10px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_log' not in st.session_state:
    st.session_state.analysis_log = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = ""

def perform_ocr(image):
    """Extract text from image using available OCR engine.

    Tries `pytesseract` first. If the Tesseract binary is not installed or
    not on PATH, falls back to `easyocr` if available. If neither is usable,
    returns an empty string and shows instructions to the user.
    """
    # Try pytesseract (requires Tesseract OCR binary installed)
    try:
        import pytesseract
        try:
            text = pytesseract.image_to_string(image)
            return text.strip()
        except pytesseract.pytesseract.TesseractNotFoundError:
            # Tesseract binary not installed or not in PATH
            st.warning("Tesseract executable not found. Trying fallback OCR...")
        except Exception as e:
            st.warning(f"pytesseract OCR failed: {e}. Trying fallback OCR...")
    except Exception:
        # pytesseract not installed at all
        st.info("`pytesseract` Python package not available. Trying fallback OCR...")

    # Fallback: try easyocr (pure-Python model; may require additional packages)
    try:
        import easyocr
    except Exception:
        st.error(
            "OCR Error: Tesseract not available and `easyocr` is not installed.\n"
            "Install Tesseract OCR (native binary) or install `easyocr` via:\n"
            "    python -m pip install easyocr\n"
            "Tesseract (Windows) installer: https://github.com/tesseract-ocr/tesseract"
        )
        return ""

    try:
        # easyocr expects a numpy array (H x W x C)
        try:
            import numpy as np
        except Exception:
            st.error("`numpy` is required by easyocr. Install with `pip install numpy`.")
            return ""

        reader = easyocr.Reader(['en'], gpu=False)
        img_arr = np.array(image.convert('RGB'))
        results = reader.readtext(img_arr)
        # results: list of (bbox, text, confidence)
        text = '\n'.join([r[1] for r in results])
        if not text.strip():
            st.info("Fallback OCR ran but returned no text. The image may be low quality.")
        return text.strip()
    except Exception as e:
        st.error(f"Fallback OCR (easyocr) error: {e}")
        return ""

# UI Layout
st.title("🏥 Multi-Agent Medical Report Analyzer")
st.markdown("**AI-powered collaborative analysis by multiple specialized medical agents**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Check for API key
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        st.success("✅ API Key loaded from .env")
    else:
        st.warning("⚠️ No API key found in .env file")
        api_key = st.text_input("Enter Groq API Key manually:", type="password")
    
    st.markdown("---")
    st.markdown("### 👥 Agent Team")
    st.markdown("**🔴 Dr. Diagnostic** - Primary Analysis")
    st.markdown("**🔵 Dr. Specialist** - Expert Consultation")
    st.markdown("**🟢 Dr. Coordinator** - Synthesis & Planning")
    st.markdown("---")
    
    if st.button("🗑️ Clear Results"):
        st.session_state.analysis_results = None
        st.session_state.analysis_log = []
        st.session_state.extracted_text = ""
        st.rerun()
    
    st.caption("⚠️ Disclaimer: This is a demo tool. Always consult real healthcare professionals.")

# Main area - Input Section
st.header("📥 Input Medical Report")

input_method = st.radio(
    "Choose input method:",
    ["✍️ Type/Paste Text", "📸 Upload Image (OCR)", "📋 Load Sample"],
    horizontal=True
)

medical_report = ""

if input_method == "✍️ Type/Paste Text":
    medical_report = st.text_area(
        "Enter medical report:",
        height=200,
        placeholder="Enter patient symptoms, vitals, lab results, physical examination findings..."
    )

elif input_method == "📸 Upload Image (OCR)":
    st.info("📌 Upload an image of a medical report. Text will be extracted automatically using OCR.")
    
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg', 'tiff', 'bmp'],
        help="Upload a clear image of a medical report"
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📷 Uploaded Image")
            image = Image.open(uploaded_file)
            st.image(image, width='stretch')
        
        with col2:
            st.subheader("📝 Extracted Text")
            if st.button("🔍 Extract Text (OCR)", type="primary"):
                with st.spinner("Extracting text from image..."):
                    extracted_text = perform_ocr(image)
                    st.session_state.extracted_text = extracted_text
            
            if st.session_state.extracted_text:
                medical_report = st.text_area(
                    "Edit extracted text if needed:",
                    value=st.session_state.extracted_text,
                    height=200
                )
            else:
                st.info("Click 'Extract Text' to process the image")

elif input_method == "📋 Load Sample":
    sample_reports = {
        "Chest Pain Emergency": """Patient: 58-year-old male
Chief Complaint: Chest pain, shortness of breath
History: Pain started 2 hours ago, radiating to left arm
Vitals: BP 150/95, HR 98, Temp 98.6°F, O2 Sat 94%
Physical: Diaphoresis noted, mild distress
Labs: Pending troponin, ECG shows ST elevation in leads II, III, aVF
Past Medical History: Hypertension, hyperlipidemia
Medications: Lisinopril 10mg, Atorvastatin 40mg""",
        
        "Diabetic Follow-up": """Patient: 45-year-old female with Type 2 DM
Chief Complaint: Routine follow-up, foot tingling
History: DM for 8 years, inconsistent medication adherence
Vitals: BP 140/88, HR 76, BMI 32, Weight 185 lbs
Labs: HbA1c 9.2%, fasting glucose 220 mg/dL, Creatinine 1.1
Physical: Decreased sensation in bilateral feet, no wounds noted
Current medications: Metformin 1000mg BID
Allergies: None known""",
        
        "Respiratory Infection": """Patient: 32-year-old female
Chief Complaint: Persistent cough, fever for 5 days
History: Productive cough with yellow sputum, chills, body aches
Vitals: BP 118/76, HR 88, Temp 101.4°F, RR 20, O2 Sat 96%
Physical: Rhonchi bilateral lower lobes, no wheezing
Labs: WBC 14,500, CRP elevated
CXR: Patchy infiltrates right lower lobe
Social: Non-smoker, works in daycare"""
    }
    
    selected_sample = st.selectbox("Select a sample case:", list(sample_reports.keys()))
    medical_report = st.text_area(
        "Medical report:",
        value=sample_reports[selected_sample],
        height=200
    )

# Analyze button
st.markdown("---")
analyze_btn = st.button("🔍 Analyze with Multi-Agent System", type="primary", width='stretch')

# Activity Log Section
with st.expander("📊 Real-time Activity Log", expanded=True):
    log_container = st.container(height=200)
    
    if st.session_state.analysis_log:
        with log_container:
            for log in st.session_state.analysis_log:
                st.markdown(f'<div class="log-entry">{log}</div>', unsafe_allow_html=True)
    else:
        st.info("Activity log will appear here during analysis...")

# Analysis execution
if analyze_btn:
    if not api_key:
        st.error("⚠️ Please provide a Groq API key in .env file or sidebar")
    elif not medical_report.strip():
        st.error("⚠️ Please enter a medical report to analyze")
    else:
        st.session_state.analysis_log = []  # Clear previous logs
        
        with st.spinner("🤖 Multi-agent analysis in progress..."):
            try:
                # Initialize agent system
                agent_system = MedicalAgentSystem(api_key)
                
                # Run analysis with logging callback
                def log_callback(agent_name, event):
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    log_entry = f"[{timestamp}] <strong>{agent_name}</strong>: {event}"
                    st.session_state.analysis_log.append(log_entry)
                
                results = agent_system.analyze_report(medical_report, log_callback)
                st.session_state.analysis_results = results
                
                st.success("✅ Analysis complete!")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                timestamp = datetime.now().strftime("%H:%M:%S")
                st.session_state.analysis_log.append(
                    f"[{timestamp}] <strong>System</strong>: Error - {str(e)}"
                )

# Display results
if st.session_state.analysis_results:
    st.markdown("---")
    st.header("📋 Multi-Agent Analysis Results")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔴 Diagnostic Agent", 
        "🔵 Specialist Agent", 
        "🟢 Coordinator Agent",
        "📄 Full Report"
    ])
    
    with tab1:
        st.markdown('<div class="agent-card diagnostic">', unsafe_allow_html=True)
        st.markdown("### Dr. Diagnostic - Primary Analysis")
        st.markdown(st.session_state.analysis_results['diagnostic'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="agent-card specialist">', unsafe_allow_html=True)
        st.markdown("### Dr. Specialist - Expert Consultation")
        st.markdown(st.session_state.analysis_results['specialist'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="agent-card coordinator">', unsafe_allow_html=True)
        st.markdown("### Dr. Coordinator - Unified Care Plan")
        st.markdown(st.session_state.analysis_results['coordinator'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### Complete Multi-Agent Report")
        
        report_text = f"""MULTI-AGENT MEDICAL ANALYSIS REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{'='*70}
ORIGINAL MEDICAL REPORT
{'='*70}
{medical_report}

{'='*70}
DIAGNOSTIC AGENT ANALYSIS (Dr. Diagnostic)
{'='*70}
{st.session_state.analysis_results['diagnostic']}

{'='*70}
SPECIALIST CONSULTATION (Dr. Specialist)
{'='*70}
{st.session_state.analysis_results['specialist']}

{'='*70}
COORDINATOR SYNTHESIS (Dr. Coordinator)
{'='*70}
{st.session_state.analysis_results['coordinator']}

{'='*70}
END OF REPORT
{'='*70}
"""
        # Sanitize report for download: remove markdown bold markers and tidy blank lines
        def _sanitize_report(text: str) -> str:
            if not isinstance(text, str):
                return text
            # Remove markdown bold markers
            text = text.replace('**', '')
            # Collapse 3+ newlines into 2
            text = re.sub(r'\n{3,}', '\n\n', text)
            # Trim trailing whitespace on each line
            text = '\n'.join(line.rstrip() for line in text.splitlines())
            # Trim leading/trailing whitespace
            return text.strip() + '\n'

        report_text_clean = _sanitize_report(report_text)

        st.text_area("Full Report Preview", report_text_clean, height=400)

        st.download_button(
            label="📥 Download Complete Report",
            data=report_text_clean,
            file_name=f"medical_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            key="download_clean_report",
            width='stretch'
        )
