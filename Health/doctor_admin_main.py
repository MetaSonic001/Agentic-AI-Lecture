import streamlit as st
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
from pathlib import Path

# Import our modules
from agents.extraction_agent import ExtractionAgent
from agents.admin_agent import AdminAgent
from utils.logger import setup_logger
from utils.database import Database

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger()

# Page configuration
st.set_page_config(
    page_title="Doctor's Admin Automator",
    page_icon="🩺",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .step-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'extraction_result' not in st.session_state:
        st.session_state.extraction_result = None
    if 'admin_result' not in st.session_state:
        st.session_state.admin_result = None
    if 'processing_logs' not in st.session_state:
        st.session_state.processing_logs = []
    if 'db' not in st.session_state:
        st.session_state.db = Database()

def display_header():
    """Display application header"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🩺 Doctor's Admin Automator")
        st.markdown("*Automate patient documentation, prescriptions, and scheduling*")
    with col2:
        st.metric("Total Patients", st.session_state.db.get_patient_count())

def process_doctor_note(note, patient_name, patient_age):
    """Process doctor's note through the agent pipeline"""
    st.session_state.processing_logs = []
    
    try:
        # Step 1: Extraction Agent
        with st.spinner("🔍 Extracting information..."):
            st.session_state.processing_logs.append({
                "step": "Extraction Agent",
                "status": "running",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            extraction_agent = ExtractionAgent()
            extraction_result = extraction_agent.extract(note, patient_name, patient_age)
            
            st.session_state.extraction_result = extraction_result
            st.session_state.processing_logs.append({
                "step": "Extraction Agent",
                "status": "completed",
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "data": extraction_result
            })
            logger.info(f"Extraction completed for patient: {patient_name}")
        
        # Step 2: Admin Agent
        with st.spinner("📋 Processing administrative tasks..."):
            st.session_state.processing_logs.append({
                "step": "Admin Agent",
                "status": "running",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            admin_agent = AdminAgent(st.session_state.db)
            admin_result = admin_agent.process(extraction_result)
            
            st.session_state.admin_result = admin_result
            st.session_state.processing_logs.append({
                "step": "Admin Agent",
                "status": "completed",
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "data": admin_result
            })
            logger.info(f"Admin processing completed for patient: {patient_name}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error processing note: {str(e)}")
        st.error(f"Error: {str(e)}")
        return False

def display_input_section():
    """Display the input section for doctor's notes"""
    st.header("📝 Patient Visit Notes")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        note = st.text_area(
            "Doctor's Note",
            placeholder="Enter patient symptoms, diagnosis, and treatment plan...\n\nExample: Patient complaining of high fever and cough for 3 days. Temperature 101F. Diagnosed with viral fever. Prescribed paracetamol 500mg twice daily for 5 days. Follow up in 7 days.",
            height=200
        )
    
    with col2:
        patient_name = st.text_input("Patient Name", placeholder="John Doe")
        patient_age = st.number_input("Patient Age", min_value=1, max_value=120, value=30)
        
    if st.button("🚀 Process Note", type="primary", use_container_width=True):
        if not note or not patient_name:
            st.warning("Please fill in all required fields")
        else:
            success = process_doctor_note(note, patient_name, patient_age)
            if success:
                st.success("✅ Processing completed successfully!")
                st.rerun()

def display_processing_logs():
    """Display step-by-step processing logs"""
    if st.session_state.processing_logs:
        st.header("🔄 Processing Steps")
        
        for log in st.session_state.processing_logs:
            with st.expander(f"{log['step']} - {log['status'].upper()} at {log['timestamp']}", expanded=True):
                if log['status'] == 'running':
                    st.info("⏳ In progress...")
                elif log['status'] == 'completed':
                    st.success("✅ Completed")
                    if 'data' in log:
                        st.json(log['data'])

def display_results():
    """Display final results"""
    if st.session_state.admin_result:
        st.header("📊 Results")
        
        result = st.session_state.admin_result
        
        # Summary Card
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown(f"### {result.get('summary', 'Processing completed')}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Results in tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📋 EHR Record", "💊 Prescription", "📅 Appointment", "📧 Notifications"])
        
        with tab1:
            if result.get('ehr_status') == 'success':
                st.success("✅ EHR Record Created")
                st.json(result.get('ehr_data', {}))
            else:
                st.error("❌ EHR Record Failed")
        
        with tab2:
            if result.get('prescription_status') == 'success':
                st.success("✅ Prescription Generated")
                st.markdown(f"**File:** `{result.get('prescription_file', 'N/A')}`")
                if result.get('prescription_data'):
                    st.json(result['prescription_data'])
            else:
                st.error("❌ Prescription Generation Failed")
        
        with tab3:
            if result.get('appointment_status') == 'success':
                st.success("✅ Appointment Scheduled")
                appt = result.get('appointment_data', {})
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Date:** {appt.get('date', 'N/A')}")
                    st.markdown(f"**Time:** {appt.get('time', 'N/A')}")
                with col2:
                    st.markdown(f"**Type:** {appt.get('type', 'N/A')}")
                    st.markdown(f"**Status:** {appt.get('status', 'N/A')}")
            else:
                st.error("❌ Appointment Scheduling Failed")
        
        with tab4:
            if result.get('notification_status') == 'success':
                st.success("✅ Notifications Sent")
                notifs = result.get('notifications', [])
                for notif in notifs:
                    st.info(f"📧 {notif}")
            else:
                st.warning("⚠️ No notifications sent")

def display_patient_history():
    """Display patient history from database"""
    st.header("📚 Patient Records")
    
    patients = st.session_state.db.get_all_patients()
    
    if patients:
        for patient in patients:
            with st.expander(f"👤 {patient['name']} (Age: {patient['age']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Diagnosis:** {patient.get('diagnosis', 'N/A')}")
                    st.markdown(f"**Date:** {patient.get('date', 'N/A')}")
                with col2:
                    if patient.get('vitals'):
                        st.markdown("**Vitals:**")
                        st.json(patient['vitals'])
    else:
        st.info("No patient records yet")

def main():
    """Main application function"""
    initialize_session_state()
    display_header()
    
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2382/2382461.png", width=100)
        st.markdown("---")
        st.markdown("### 🔧 Settings")
        
        if st.button("🗑️ Clear Session"):
            st.session_state.extraction_result = None
            st.session_state.admin_result = None
            st.session_state.processing_logs = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        This system automates:
        - 📋 EHR documentation
        - 💊 Prescription generation
        - 📅 Appointment scheduling
        - 📧 Patient reminders
        """)
    
    # Main content
    display_input_section()
    
    st.markdown("---")
    
    # Processing logs and results
    col1, col2 = st.columns([1, 1])
    
    with col1:
        display_processing_logs()
    
    with col2:
        display_results()
    
    st.markdown("---")
    display_patient_history()

if __name__ == "__main__":
    main()