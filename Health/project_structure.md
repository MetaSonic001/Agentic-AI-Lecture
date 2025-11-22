# 📁 Complete Project Structure

Here's the complete directory structure for the Doctor's Admin Automator project:

```
doctor-admin-automator/
│
├── 📄 main.py                          # Main Streamlit application entry point
├── 📄 setup.py                         # Setup script for initialization
├── 📄 requirements.txt                 # Python package dependencies
├── 📄 .env.example                     # Environment variables template
├── 📄 .env                             # Your actual environment variables (not in git)
├── 📄 .gitignore                       # Git ignore configuration
├── 📄 README.md                        # Main documentation
├── 📄 QUICKSTART.md                    # Quick start guide
├── 📄 PROJECT_STRUCTURE.md             # This file
│
├── 📁 agents/                          # AI Agents implementations
│   ├── 📄 __init__.py                  # Package initialization
│   ├── 📄 extraction_agent.py          # Extraction Agent (medical info extraction)
│   └── 📄 admin_agent.py               # Admin Agent (EHR, scheduling, notifications)
│
├── 📁 utils/                           # Utility modules
│   ├── 📄 __init__.py                  # Package initialization
│   ├── 📄 logger.py                    # Logging configuration and setup
│   ├── 📄 database.py                  # SQLite database manager
│   ├── 📄 pdf_generator.py             # PDF prescription generator (ReportLab)
│   ├── 📄 calendar_manager.py          # Appointment scheduling manager
│   └── 📄 notification_service.py      # Notification service (email/SMS mock)
│
├── 📁 data/                            # Data storage (created at runtime)
│   ├── 📄 .gitkeep                     # Keep directory in git
│   ├── 📄 medical_records.db           # SQLite database (patients & appointments)
│   ├── 📄 appointments.json            # Appointment data (JSON backup)
│   └── 📄 notifications.json           # Notification logs
│
├── 📁 logs/                            # Application logs (created at runtime)
│   ├── 📄 .gitkeep                     # Keep directory in git
│   └── 📄 doctor_admin_YYYYMMDD.log    # Daily log files
│
└── 📁 prescriptions/                   # Generated prescription PDFs
    ├── 📄 .gitkeep                     # Keep directory in git
    └── 📄 PatientName_DateTime.pdf     # Generated prescriptions
```

## 📋 File Descriptions

### Root Level Files

#### `main.py` (Application Core)
- **Purpose:** Main Streamlit web application
- **Key Functions:**
  - `initialize_session_state()` - Initialize session variables
  - `display_header()` - Render app header
  - `process_doctor_note()` - Main processing pipeline
  - `display_input_section()` - Patient input form
  - `display_processing_logs()` - Real-time step viewer
  - `display_results()` - Results dashboard
  - `display_patient_history()` - Patient records viewer

#### `setup.py` (Setup Script)
- **Purpose:** Initialize project structure
- **Functions:**
  - `create_directory_structure()` - Create folders
  - `check_env_file()` - Verify .env exists
  - `verify_installation()` - Check dependencies

#### `requirements.txt` (Dependencies)
```
streamlit           # Web UI framework
crewai             # Multi-agent orchestration
langchain-groq     # Groq LLM integration
python-dotenv      # Environment variable management
reportlab          # PDF generation
```

#### `.env.example` (Configuration Template)
- Template for environment variables
- Shows required and optional configurations
- Not tracked in git

#### `.env` (Your Configuration)
- Contains your actual API keys
- NEVER commit this to git
- Required: `GROQ_API_KEY`

### Agents Directory (`agents/`)

#### `extraction_agent.py`
- **Class:** `ExtractionAgent`
- **Purpose:** Extract structured medical information from doctor's notes
- **Key Methods:**
  - `create_agent()` - Initialize CrewAI agent
  - `create_extraction_task()` - Define extraction task
  - `extract()` - Execute extraction process
  - `_create_fallback_structure()` - Fallback for parsing errors
- **LLM:** Groq (Mixtral-8x7B)
- **Output:** JSON with patient info, diagnosis, vitals, prescription, follow-up

#### `admin_agent.py`
- **Class:** `AdminAgent`
- **Purpose:** Handle all administrative tasks
- **Key Methods:**
  - `create_agent()` - Initialize admin agent
  - `process()` - Execute all admin tasks
  - `_fill_ehr()` - Save to database
  - `_generate_prescription()` - Create PDF
  - `_schedule_appointment()` - Book appointment
  - `_send_notifications()` - Send reminders
  - `_generate_summary()` - Create visit summary
- **Integrations:** Database, PDF, Calendar, Notifications

### Utils Directory (`utils/`)

#### `logger.py`
- **Function:** `setup_logger()`
- **Purpose:** Configure application logging
- **Features:**
  - Dual output (console + file)
  - Daily log rotation
  - Detailed formatting with timestamps
  - Function name and line number tracking

#### `database.py`
- **Class:** `Database`
- **Purpose:** SQLite database management
- **Tables:**
  - `patients` - Patient records with medical info
  - `appointments` - Scheduled appointments
- **Key Methods:**
  - `add_patient_record()` - Insert patient
  - `add_appointment()` - Insert appointment
  - `get_all_patients()` - Retrieve patients
  - `get_patient_count()` - Count unique patients

#### `pdf_generator.py`
- **Function:** `generate_prescription_pdf()`
- **Purpose:** Create professional prescription PDFs
- **Library:** ReportLab
- **Features:**
  - Professional layout
  - Patient information section
  - Medication table
  - Follow-up instructions
  - Footer with disclaimers

#### `calendar_manager.py`
- **Class:** `CalendarManager`
- **Purpose:** Appointment scheduling
- **Storage:** JSON file (`data/appointments.json`)
- **Key Methods:**
  - `schedule_appointment()` - Create appointment
  - `parse_followup_period()` - Convert "7 days" to date
  - `get_upcoming_appointments()` - Get future appointments
  - `cancel_appointment()` - Cancel booking
- **Note:** Mock implementation, extendable to Google Calendar

#### `notification_service.py`
- **Class:** `NotificationService`
- **Purpose:** Send patient notifications
- **Storage:** JSON file (`data/notifications.json`)
- **Key Methods:**
  - `send_appointment_reminder()` - Appointment SMS/email
  - `send_prescription_notification()` - Prescription details
  - `send_followup_reminder()` - Follow-up reminder
  - `get_notifications_for_patient()` - Get patient notifications
- **Note:** Mock implementation, extendable to Twilio/SMTP

### Data Directory (`data/`)

#### `medical_records.db` (SQLite Database)
- **Schema:**
  ```sql
  patients (
    id, name, age, diagnosis, symptoms, 
    vitals, prescription, followup, date, created_at
  )
  
  appointments (
    id, patient_name, appointment_date, 
    appointment_time, appointment_type, status, created_at
  )
  ```

#### `appointments.json` (JSON Backup)
- Stores appointment data
- Used by CalendarManager
- Example:
  ```json
  [
    {
      "id": "1",
      "patient_name": "John Doe",
      "date": "2024-12-01",
      "time": "09:00 AM",
      "type": "routine",
      "status": "scheduled"
    }
  ]
  ```

#### `notifications.json` (Notification Log)
- Logs all sent notifications
- Example:
  ```json
  [
    {
      "id": "1",
      "type": "appointment_reminder",
      "patient_name": "John Doe",
      "message": "Appointment reminder...",
      "timestamp": "2024-11-23T10:30:00"
    }
  ]
  ```

### Logs Directory (`logs/`)

#### Daily Log Files
- Format: `doctor_admin_YYYYMMDD.log`
- Contains:
  - Timestamp of each action
  - Log level (INFO, WARNING, ERROR)
  - Function and line number
  - Detailed message
- Example:
  ```
  2024-11-23 10:30:15 - doctor_admin - INFO - extraction_agent.py:45 - Starting extraction for patient: John Doe
  ```

### Prescriptions Directory (`prescriptions/`)

#### Generated PDFs
- Format: `PatientName_YYYYMMDD_HHMMSS.pdf`
- Example: `John_Doe_20241123_103045.pdf`
- Contains:
  - Patient information
  - Diagnosis
  - Medication table
  - Follow-up instructions
  - Professional formatting

## 🔄 Data Flow

```
User Input (main.py)
    ↓
Extraction Agent (agents/extraction_agent.py)
    ↓
Structured JSON
    ↓
Admin Agent (agents/admin_agent.py)
    ├── Database (utils/database.py) → SQLite
    ├── PDF Generator (utils/pdf_generator.py) → PDF file
    ├── Calendar Manager (utils/calendar_manager.py) → JSON
    ├── Notification Service (utils/notification_service.py) → JSON
    └── Logger (utils/logger.py) → Log file
    ↓
Results Display (main.py)
```

## 📦 Dependencies Explained

| Package | Purpose | Version |
|---------|---------|---------|
| `streamlit` | Web UI framework | Latest |
| `crewai` | Multi-agent orchestration | Latest |
| `langchain-groq` | Groq LLM integration | Latest |
| `python-dotenv` | Environment variables | Latest |
| `reportlab` | PDF generation | Latest |
| `sqlite3` | Database (built-in) | Built-in |

## 🔧 Configuration Files

### `.env` (Environment Variables)
```bash
# Required
GROQ_API_KEY=gsk_...

# Optional (for extensions)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
TWILIO_ACCOUNT_SID=...
```

### `.gitignore` (Git Exclusions)
```
.env                    # Never commit API keys
__pycache__/            # Python cache
data/*.db               # Database files
data/*.json             # JSON data
logs/*.log              # Log files
prescriptions/*.pdf     # Generated PDFs
```

## 📊 Size Estimates

- **Code:** ~2,500 lines
- **Database:** ~1MB per 100 patients
- **Logs:** ~100KB per day
- **PDFs:** ~50KB per prescription
- **Total (empty):** <1MB
- **Total (100 patients):** ~5MB

## 🎯 Extension Points

Want to extend the system? Here are the key files to modify:

1. **Add new agent:** Create in `agents/`
2. **Add utility:** Create in `utils/`
3. **Modify UI:** Edit `main.py`
4. **Change database schema:** Edit `utils/database.py`
5. **Customize PDF:** Edit `utils/pdf_generator.py`
6. **Add integrations:** Extend `utils/calendar_manager.py` or `utils/notification_service.py`

## ✅ Checklist for New Setup

- [ ] All files created in correct locations
- [ ] `agents/__init__.py` present
- [ ] `utils/__init__.py` present
- [ ] `.env` file created with API key
- [ ] `data/`, `logs/`, `prescriptions/` directories exist
- [ ] `requirements.txt` dependencies installed
- [ ] `python setup.py` runs successfully
- [ ] `streamlit run main.py` starts app

---

This structure is designed for:
- ✅ Easy navigation
- ✅ Clear separation of concerns
- ✅ Extensibility
- ✅ Professional code organization