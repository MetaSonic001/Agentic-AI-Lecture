# 🚀 Quick Start Guide

Get up and running in 5 minutes!

## 📋 Prerequisites

- Python 3.8 or higher
- A Groq API key (free from [console.groq.com](https://console.groq.com/))

## 🔧 Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:

```
GROQ_API_KEY=your_actual_api_key_here
```

### 3. Initialize Project

```bash
python setup.py
```

This will:
- Create necessary directories (data/, logs/, prescriptions/)
- Verify all packages are installed
- Check your environment configuration

### 4. Run the Application

```bash
streamlit run main.py
```

The app will open automatically at `http://localhost:8501`

## 🎯 First Test

Try this sample input:

**Patient Name:** John Doe  
**Patient Age:** 35  
**Doctor's Note:**
```
Patient presenting with acute fever (103°F) and persistent cough for 4 days. 
Blood pressure 130/85, heart rate 88 bpm. 
Chest clear on auscultation. Throat appears red and inflamed.

Diagnosis: Upper Respiratory Tract Infection (URTI)

Treatment Plan:
- Azithromycin 500mg once daily for 5 days
- Paracetamol 650mg as needed for fever (max 3 times daily)
- Plenty of fluids and rest

Follow-up: Schedule appointment in 7 days if symptoms persist
```

Click **"🚀 Process Note"** and watch the magic happen!

## 📊 What You'll See

1. **Processing Steps** (left panel):
   - Extraction Agent analyzing the note
   - Admin Agent processing tasks
   - Real-time status updates

2. **Results** (right panel):
   - Summary of the visit
   - EHR record (JSON format)
   - Generated prescription
   - Scheduled appointment
   - Sent notifications

3. **Patient Records** (bottom):
   - All historical patient records
   - Expandable cards with details

## 🔍 Where to Find Generated Files

- **Database:** `data/medical_records.db`
- **Prescriptions:** `prescriptions/PatientName_DateTime.pdf`
- **Appointments:** `data/appointments.json`
- **Notifications:** `data/notifications.json`
- **Logs:** `logs/doctor_admin_YYYYMMDD.log`

## 🎨 UI Features

### Main Dashboard
- **Input Section:** Enter patient details and doctor's notes
- **Processing Logs:** Real-time step-by-step execution
- **Results Tabs:** View EHR, prescription, appointment, and notifications
- **Patient History:** Browse all past records

### Sidebar
- **Patient Count:** Total unique patients
- **Clear Session:** Reset current processing
- **About Section:** Quick feature overview

## 💡 Tips

1. **Be Descriptive:** More detailed notes = better extraction
2. **Include Vitals:** Temperature, BP, heart rate improve accuracy
3. **Specify Duration:** Clear medication duration helps scheduling
4. **Follow-up Period:** Use formats like "7 days", "2 weeks", "1 month"

## ⚡ Sample Notes Templates

### Fever & Cough
```
Patient has high fever (101°F) and dry cough for 3 days. 
BP 120/80. Diagnosed with viral fever.
Prescribed paracetamol 500mg twice daily for 5 days.
Follow up in 7 days.
```

### Diabetes Follow-up
```
Patient with Type 2 Diabetes for routine check. 
Fasting glucose 140 mg/dL. BP 135/85. 
Continue Metformin 500mg twice daily.
Advised diet control and exercise.
Follow up in 1 month.
```

### Injury Assessment
```
Patient fell and injured right knee. Swelling and pain present.
No fracture on examination. Applied ice pack.
Prescribed Ibuprofen 400mg three times daily for 3 days.
Rest and elevation advised.
Follow up in 5 days or if pain worsens.
```

## 🐛 Common Issues

### "Invalid API Key"
- Double-check your Groq API key
- Ensure no extra spaces in `.env` file
- Restart the app after changing `.env`

### "Import Error"
```bash
pip install --upgrade -r requirements.txt
```

### "Port Already in Use"
```bash
streamlit run main.py --server.port 8502
```

## 📚 Next Steps

- Explore the **README.md** for detailed documentation
- Check **logs/** for detailed execution traces
- Customize the UI in **main.py**
- Extend agents in **agents/** directory

## 🎉 You're Ready!

Your Doctor's Admin Automator is now ready to streamline your healthcare workflow!

For questions or issues, check the logs in `logs/` or refer to the main README.md.

---

**Happy Automating! 🩺✨**