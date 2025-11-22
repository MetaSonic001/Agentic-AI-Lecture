# 🧪 Testing Guide

Comprehensive testing guide for the Doctor's Admin Automator.

## 📋 Pre-Testing Checklist

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with valid `GROQ_API_KEY`
- [ ] Run `python setup.py` successfully
- [ ] Application starts with `streamlit run main.py`

## 🎯 Test Scenarios

### Test 1: Basic Fever Case

**Input:**
- Patient Name: `Sarah Johnson`
- Patient Age: `28`
- Doctor's Note:
```
Patient presenting with fever of 102°F for 2 days. 
Mild headache and body aches. 
No cough or breathing difficulty.
BP: 118/76, HR: 82 bpm

Diagnosis: Viral Fever

Treatment:
- Paracetamol 500mg, take twice daily for 5 days
- Plenty of rest and hydration

Follow-up in 7 days if symptoms persist
```

**Expected Results:**
- ✅ Extraction: Fever identified, vitals captured
- ✅ Diagnosis: Viral Fever
- ✅ Prescription: Paracetamol with correct dosage
- ✅ Appointment: Scheduled 7 days from today
- ✅ Notifications: Appointment reminder and prescription details

---

### Test 2: Complex Multi-Medication Case

**Input:**
- Patient Name: `Michael Chen`
- Patient Age: `55`
- Doctor's Note:
```
Patient with Type 2 Diabetes for routine checkup.
Fasting glucose: 145 mg/dL
BP: 140/90 mmHg, HR: 78 bpm
Weight: 85kg, BMI: 28.5

Diagnosis: Type 2 Diabetes with Hypertension

Treatment Plan:
- Metformin 500mg twice daily (continue)
- Amlodipine 5mg once daily in morning
- Atorvastatin 10mg once daily at night

Lifestyle modifications:
- Low carb diet
- 30 minutes walking daily
- Reduce salt intake

Follow-up appointment in 1 month for glucose monitoring
```

**Expected Results:**
- ✅ Multiple medications extracted correctly
- ✅ All vitals captured (glucose, BP, HR, weight, BMI)
- ✅ Follow-up scheduled for 1 month
- ✅ PDF includes all 3 medications with proper timing
- ✅ Diagnosis: Type 2 Diabetes with Hypertension

---

### Test 3: Injury/Emergency Case

**Input:**
- Patient Name: `Emily Rodriguez`
- Patient Age: `32`
- Doctor's Note:
```
Patient slipped and fell, injured left ankle.
Swelling and pain present, difficulty walking.
No visible deformity, likely sprain.
Temp: Normal, BP: 125/82

Diagnosis: Left Ankle Sprain (Grade 2)

Immediate Treatment:
- Applied ice pack
- Ankle wrapped with elastic bandage

Medications:
- Ibuprofen 400mg three times daily after meals for 5 days
- Apply ice 3-4 times daily

Instructions:
- Rest and elevate leg
- No weight bearing for 48 hours
- Use crutches if needed

Urgent follow-up in 3 days
```

**Expected Results:**
- ✅ Urgent appointment type identified
- ✅ Follow-up scheduled for 3 days
- ✅ Prescription includes Ibuprofen with meal instructions
- ✅ Diagnosis: Left Ankle Sprain

---

### Test 4: Pediatric Case

**Input:**
- Patient Name: `Tommy Williams`
- Patient Age: `8`
- Doctor's Note:
```
Child brought in with sore throat and fever.
Temperature: 101.5°F
Throat: Red and inflamed
Enlarged tonsils with white patches
No difficulty breathing

Diagnosis: Acute Tonsillitis

Treatment:
- Amoxicillin 250mg oral suspension, 5ml twice daily for 7 days
- Ibuprofen 200mg as needed for fever/pain (max 3 times daily)

Instructions:
- Plenty of fluids
- Soft foods
- Rest at home for 2-3 days

Review in 5 days or earlier if worsening symptoms
```

**Expected Results:**
- ✅ Age-appropriate medication dosage
- ✅ Pediatric diagnosis handled correctly
- ✅ Instructions included in prescription
- ✅ Follow-up in 5 days

---

### Test 5: Minimal Information Case

**Input:**
- Patient Name: `David Brown`
- Patient Age: `42`
- Doctor's Note:
```
Routine health check. All vitals normal. No concerns. Continue current lifestyle.
```

**Expected Results:**
- ✅ Handles minimal information gracefully
- ✅ No prescription needed (empty array)
- ✅ Routine appointment type
- ✅ Default follow-up period applied

---

## 🔍 Component Testing

### Test Database Functions

```python
# Test in Python console
from utils.database import Database

db = Database()

# Test patient count
count = db.get_patient_count()
print(f"Total patients: {count}")

# Test get all patients
patients = db.get_all_patients()
for patient in patients:
    print(f"Patient: {patient['name']}, Age: {patient['age']}")
```

### Test PDF Generation

```python
from utils.pdf_generator import generate_prescription_pdf

test_data = {
    "patient": {"name": "Test Patient", "age": 30},
    "diagnosis": "Test Diagnosis",
    "prescription": [
        {
            "medication": "Test Med",
            "dosage": "500mg",
            "frequency": "Twice daily",
            "duration": "5 days"
        }
    ],
    "followup": "7 days"
}

filename = generate_prescription_pdf(test_data)
print(f"PDF created: prescriptions/{filename}")
```

### Test Calendar Manager

```python
from utils.calendar_manager import CalendarManager

cal = CalendarManager()

# Test scheduling
appointment = cal.schedule_appointment(
    patient_name="Test Patient",
    followup_period="7 days",
    appointment_type="routine"
)
print(f"Appointment: {appointment}")

# Test getting appointments
upcoming = cal.get_upcoming_appointments()
print(f"Upcoming appointments: {len(upcoming)}")
```

### Test Notification Service

```python
from utils.notification_service import NotificationService

notif = NotificationService()

# Test appointment reminder
result = notif.send_appointment_reminder(
    patient_name="Test Patient",
    appointment_date="2024-12-01",
    appointment_time="09:00 AM"
)
print(f"Notification: {result}")
```

---

## 📊 Verification Checklist

After each test, verify:

### UI Checks
- [ ] Input form renders correctly
- [ ] Process button is clickable
- [ ] Loading spinner appears during processing
- [ ] Processing logs show up in left panel
- [ ] Results tabs display properly
- [ ] Patient history updates at bottom

### Data Checks
- [ ] Database file created in `data/`
- [ ] Patient record saved with all fields
- [ ] Prescription PDF created in `prescriptions/`
- [ ] Appointment saved in `data/appointments.json`
- [ ] Notifications logged in `data/notifications.json`

### Log Checks
- [ ] Log file created in `logs/`
- [ ] All agent actions logged
- [ ] Timestamps are correct
- [ ] Error handling logged properly

### Output Quality
- [ ] Extracted data is accurate
- [ ] Prescription PDF is readable
- [ ] All medications listed correctly
- [ ] Follow-up date calculated properly
- [ ] Notifications contain correct information

---

## 🐛 Error Scenarios to Test

### Test 1: Empty Input
- Leave patient name empty
- **Expected:** Warning message, no processing

### Test 2: Invalid API Key
- Set wrong API key in `.env`
- **Expected:** Clear error message about API key

### Test 3: Very Long Note
- Paste a 2000-word medical note
- **Expected:** Should handle gracefully, may truncate

### Test 4: Special Characters
- Use patient name: `O'Brien-Smith`
- **Expected:** Handle special characters correctly

### Test 5: No Prescription Needed
- Note with no medication mentioned
- **Expected:** Empty prescription array, but other tasks complete

---

## 📈 Performance Testing

### Load Test
1. Process 10 patients in sequence
2. Check response times
3. Verify database doesn't slow down
4. Check memory usage

**Acceptable Performance:**
- Processing time: 5-15 seconds per note
- UI remains responsive
- No memory leaks

### Concurrent Users
1. Open 3 browser tabs
2. Process different patients simultaneously
3. Verify no data mixing
4. Check logs for errors

---

## 🔧 Debugging Tips

### Check Logs First
```bash
# View latest log
tail -f logs/doctor_admin_$(date +%Y%m%d).log

# Search for errors
grep ERROR logs/*.log
```

### Verify Database
```bash
# Check database
sqlite3 data/medical_records.db

# List all patients
SELECT * FROM patients;

# List appointments
SELECT * FROM appointments;
```

### Inspect JSON Files
```bash
# View appointments
cat data/appointments.json | python -m json.tool

# View notifications
cat data/notifications.json | python -m json.tool
```

### Check PDF Output
```bash
# List generated PDFs
ls -lh prescriptions/

# Open latest PDF (macOS)
open prescriptions/$(ls -t prescriptions/ | head -1)
```

---

## ✅ Test Report Template

Use this template to document your testing:

```markdown
## Test Session: [Date]

### Environment
- Python Version: 
- OS: 
- Groq API: Working/Not Working

### Test Results

| Test # | Patient Name | Status | Issues |
|--------|-------------|--------|--------|
| 1      | Sarah Johnson | ✅ Pass | None   |
| 2      | Michael Chen  | ✅ Pass | None   |
| 3      | Emily Rodriguez | ⚠️ Warning | Minor formatting issue |

### Issues Found
1. [Issue description]
   - Severity: High/Medium/Low
   - Steps to reproduce: 
   - Expected: 
   - Actual: 

### Recommendations
- [ ] Action item 1
- [ ] Action item 2

### Overall Assessment
- Functionality: ⭐⭐⭐⭐⭐
- Performance: ⭐⭐⭐⭐⭐
- UI/UX: ⭐⭐⭐⭐⭐
- Reliability: ⭐⭐⭐⭐⭐
```

---

## 🎯 Acceptance Criteria

The system passes testing if:

✅ **Core Functionality**
- Extracts medical information with >90% accuracy
- Generates valid PDFs for all prescriptions
- Schedules appointments correctly
- Logs all notifications

✅ **Data Integrity**
- All patient records saved to database
- No data loss during processing
- JSON files remain valid

✅ **User Experience**
- Responsive UI (no freezing)
- Clear error messages
- Intuitive workflow
- Step-by-step visibility

✅ **Reliability**
- Handles edge cases gracefully
- No crashes on invalid input
- Consistent behavior across sessions

✅ **Performance**
- Processes notes in <15 seconds
- Handles 50+ patients without issues
- Low memory footprint (<500MB)

---

## 📞 Reporting Issues

If you find bugs:

1. Check logs: `logs/doctor_admin_YYYYMMDD.log`
2. Note the exact steps to reproduce
3. Include sample input that caused the issue
4. Attach relevant log entries
5. Specify your environment (OS, Python version)

---

**Happy Testing! 🧪✨**