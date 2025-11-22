import json
import os
from datetime import datetime, timedelta
from crewai import Agent, Task, Crew
from langchain_groq import ChatGroq
from utils.logger import setup_logger
from utils.pdf_generator import generate_prescription_pdf
from utils.calendar_manager import CalendarManager
from utils.notification_service import NotificationService

logger = setup_logger()

class AdminAgent:
    """Agent responsible for administrative tasks: EHR, prescriptions, scheduling, notifications"""
    
    def __init__(self, database):
        self.llm = ChatGroq(
            temperature=0,
            model_name="mixtral-8x7b-32768",
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.database = database
        self.calendar_manager = CalendarManager()
        self.notification_service = NotificationService()
        logger.info("Admin Agent initialized")
    
    def create_agent(self):
        """Create the admin agent"""
        return Agent(
            role="Medical Administrator",
            goal="Manage all administrative tasks including EHR updates, prescription generation, appointment scheduling, and patient notifications",
            backstory="""You are a highly efficient medical administrator with expertise in healthcare operations. 
            You ensure all documentation is accurate, prescriptions are properly formatted, appointments are 
            scheduled appropriately, and patients receive timely notifications.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def create_admin_task(self, agent, extracted_data):
        """Create the admin task"""
        patient_name = extracted_data['patient']['name']
        diagnosis = extracted_data['diagnosis']
        
        return Task(
            description=f"""
            Perform all administrative tasks for the patient visit:
            
            Patient Data: {json.dumps(extracted_data, indent=2)}
            
            Generate a summary that includes:
            1. Brief summary of the visit
            2. Next steps for the patient
            3. Any special instructions
            
            Format: "Patient [Name] diagnosed with [Diagnosis]. [Prescription details]. [Follow-up information]."
            """,
            agent=agent,
            expected_output="A clear summary of all administrative actions taken"
        )
    
    def process(self, extracted_data):
        """Execute all administrative tasks"""
        patient_name = extracted_data['patient']['name']
        logger.info(f"Starting admin processing for patient: {patient_name}")
        
        results = {
            'patient_name': patient_name,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Task 1: Fill EHR
            ehr_result = self._fill_ehr(extracted_data)
            results['ehr_status'] = 'success' if ehr_result else 'failed'
            results['ehr_data'] = extracted_data
            logger.info(f"EHR filling: {'success' if ehr_result else 'failed'}")
            
            # Task 2: Generate Prescription
            prescription_result = self._generate_prescription(extracted_data)
            results['prescription_status'] = 'success' if prescription_result else 'failed'
            results['prescription_file'] = prescription_result if prescription_result else None
            results['prescription_data'] = extracted_data.get('prescription', [])
            logger.info(f"Prescription generation: {'success' if prescription_result else 'failed'}")
            
            # Task 3: Schedule Appointment
            appointment_result = self._schedule_appointment(extracted_data)
            results['appointment_status'] = 'success' if appointment_result else 'failed'
            results['appointment_data'] = appointment_result if appointment_result else {}
            logger.info(f"Appointment scheduling: {'success' if appointment_result else 'failed'}")
            
            # Task 4: Send Notifications
            notification_result = self._send_notifications(extracted_data, appointment_result)
            results['notification_status'] = 'success' if notification_result else 'failed'
            results['notifications'] = notification_result if notification_result else []
            logger.info(f"Notifications: {'success' if notification_result else 'failed'}")
            
            # Task 5: Generate Summary using AI
            summary = self._generate_summary(extracted_data)
            results['summary'] = summary
            
            logger.info("Admin processing completed successfully")
            return results
        
        except Exception as e:
            logger.error(f"Admin processing failed: {str(e)}")
            results['error'] = str(e)
            return results
    
    def _fill_ehr(self, extracted_data):
        """Fill EHR record in database"""
        try:
            patient_id = self.database.add_patient_record(
                name=extracted_data['patient']['name'],
                age=extracted_data['patient']['age'],
                diagnosis=extracted_data['diagnosis'],
                symptoms=extracted_data['symptoms'],
                vitals=extracted_data['vitals'],
                prescription=extracted_data['prescription'],
                followup=extracted_data['followup']
            )
            return patient_id
        except Exception as e:
            logger.error(f"EHR filling failed: {str(e)}")
            return None
    
    def _generate_prescription(self, extracted_data):
        """Generate prescription PDF"""
        try:
            if not extracted_data.get('prescription'):
                return None
            
            filename = generate_prescription_pdf(extracted_data)
            return filename
        except Exception as e:
            logger.error(f"Prescription generation failed: {str(e)}")
            return None
    
    def _schedule_appointment(self, extracted_data):
        """Schedule appointment"""
        try:
            followup = extracted_data.get('followup', '7 days')
            appointment_type = extracted_data.get('appointment_type', 'routine')
            patient_name = extracted_data['patient']['name']
            
            appointment = self.calendar_manager.schedule_appointment(
                patient_name=patient_name,
                followup_period=followup,
                appointment_type=appointment_type
            )
            return appointment
        except Exception as e:
            logger.error(f"Appointment scheduling failed: {str(e)}")
            return None
    
    def _send_notifications(self, extracted_data, appointment_data):
        """Send notifications to patient"""
        try:
            notifications = []
            patient_name = extracted_data['patient']['name']
            
            # Appointment reminder
            if appointment_data:
                notif = self.notification_service.send_appointment_reminder(
                    patient_name=patient_name,
                    appointment_date=appointment_data.get('date'),
                    appointment_time=appointment_data.get('time')
                )
                notifications.append(notif)
            
            # Prescription notification
            if extracted_data.get('prescription'):
                notif = self.notification_service.send_prescription_notification(
                    patient_name=patient_name,
                    prescription=extracted_data['prescription']
                )
                notifications.append(notif)
            
            return notifications
        except Exception as e:
            logger.error(f"Notification sending failed: {str(e)}")
            return []
    
    def _generate_summary(self, extracted_data):
        """Generate a summary using AI"""
        try:
            agent = self.create_agent()
            task = self.create_admin_task(agent, extracted_data)
            
            crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=True
            )
            
            result = crew.kickoff()
            return str(result)
        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}")
            # Fallback summary
            patient_name = extracted_data['patient']['name']
            diagnosis = extracted_data['diagnosis']
            followup = extracted_data.get('followup', 'as needed')
            
            return f"Patient {patient_name} diagnosed with {diagnosis}. Prescription issued. Follow-up scheduled in {followup}."