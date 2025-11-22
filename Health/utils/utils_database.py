import json
import sqlite3
from datetime import datetime
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger()

class Database:
    """Database manager for storing patient records"""
    
    def __init__(self, db_path='data/medical_records.db'):
        """Initialize database connection"""
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        Path('data').mkdir(exist_ok=True)
        
        self._create_tables()
        logger.info(f"Database initialized at {db_path}")
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Patients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                diagnosis TEXT,
                symptoms TEXT,
                vitals TEXT,
                prescription TEXT,
                followup TEXT,
                date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Appointments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                appointment_type TEXT,
                status TEXT DEFAULT 'scheduled',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database tables created/verified")
    
    def add_patient_record(self, name, age, diagnosis, symptoms, vitals, prescription, followup):
        """Add a new patient record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO patients (name, age, diagnosis, symptoms, vitals, prescription, followup, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name,
                age,
                diagnosis,
                json.dumps(symptoms),
                json.dumps(vitals),
                json.dumps(prescription),
                followup,
                datetime.now().strftime('%Y-%m-%d')
            ))
            
            patient_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Patient record added: {name} (ID: {patient_id})")
            return patient_id
        
        except Exception as e:
            logger.error(f"Failed to add patient record: {str(e)}")
            return None
    
    def add_appointment(self, patient_name, appointment_date, appointment_time, appointment_type):
        """Add a new appointment"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO appointments (patient_name, appointment_date, appointment_time, appointment_type)
                VALUES (?, ?, ?, ?)
            ''', (patient_name, appointment_date, appointment_time, appointment_type))
            
            appointment_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Appointment added: {patient_name} on {appointment_date}")
            return appointment_id
        
        except Exception as e:
            logger.error(f"Failed to add appointment: {str(e)}")
            return None
    
    def get_all_patients(self, limit=10):
        """Get all patient records"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM patients 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            patients = []
            for row in rows:
                patient = dict(row)
                # Parse JSON fields
                patient['symptoms'] = json.loads(patient['symptoms']) if patient['symptoms'] else []
                patient['vitals'] = json.loads(patient['vitals']) if patient['vitals'] else {}
                patient['prescription'] = json.loads(patient['prescription']) if patient['prescription'] else []
                patients.append(patient)
            
            return patients
        
        except Exception as e:
            logger.error(f"Failed to get patients: {str(e)}")
            return []
    
    def get_patient_by_name(self, name):
        """Get patient records by name"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM patients 
                WHERE name LIKE ?
                ORDER BY created_at DESC
            ''', (f'%{name}%',))
            
            rows = cursor.fetchall()
            conn.close()
            
            patients = []
            for row in rows:
                patient = dict(row)
                patient['symptoms'] = json.loads(patient['symptoms']) if patient['symptoms'] else []
                patient['vitals'] = json.loads(patient['vitals']) if patient['vitals'] else {}
                patient['prescription'] = json.loads(patient['prescription']) if patient['prescription'] else []
                patients.append(patient)
            
            return patients
        
        except Exception as e:
            logger.error(f"Failed to get patient by name: {str(e)}")
            return []
    
    def get_patient_count(self):
        """Get total number of patients"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(DISTINCT name) FROM patients')
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
        
        except Exception as e:
            logger.error(f"Failed to get patient count: {str(e)}")
            return 0
    
    def get_upcoming_appointments(self, limit=10):
        """Get upcoming appointments"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM appointments 
                WHERE status = 'scheduled'
                ORDER BY appointment_date, appointment_time
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        
        except Exception as e:
            logger.error(f"Failed to get appointments: {str(e)}")
            return []