from datetime import datetime, timedelta
import json
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger()

class CalendarManager:
    """
    Manager for scheduling appointments
    Mock implementation that stores appointments locally
    Can be extended to integrate with Google Calendar API
    """
    
    def __init__(self, calendar_file='data/appointments.json'):
        self.calendar_file = calendar_file
        
        # Create data directory
        Path('data').mkdir(exist_ok=True)
        
        # Initialize calendar file
        if not Path(calendar_file).exists():
            self._save_appointments([])
        
        logger.info("Calendar Manager initialized")
    
    def _load_appointments(self):
        """Load appointments from file"""
        try:
            with open(self.calendar_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load appointments: {str(e)}")
            return []
    
    def _save_appointments(self, appointments):
        """Save appointments to file"""
        try:
            with open(self.calendar_file, 'w') as f:
                json.dump(appointments, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save appointments: {str(e)}")
    
    def parse_followup_period(self, followup_str):
        """
        Parse followup period string to timedelta
        
        Args:
            followup_str: String like "7 days", "2 weeks", "1 month"
        
        Returns:
            timedelta object
        """
        followup_str = followup_str.lower()
        
        try:
            # Extract number
            parts = followup_str.split()
            if len(parts) >= 2:
                number = int(parts[0])
                unit = parts[1]
                
                if 'day' in unit:
                    return timedelta(days=number)
                elif 'week' in unit:
                    return timedelta(weeks=number)
                elif 'month' in unit:
                    return timedelta(days=number * 30)  # Approximate
                elif 'year' in unit:
                    return timedelta(days=number * 365)  # Approximate
        except:
            pass
        
        # Default to 7 days
        return timedelta(days=7)
    
    def schedule_appointment(self, patient_name, followup_period, appointment_type='routine'):
        """
        Schedule an appointment
        
        Args:
            patient_name: Name of the patient
            followup_period: String describing follow-up period
            appointment_type: Type of appointment
        
        Returns:
            dict: Appointment details
        """
        try:
            # Calculate appointment date
            delta = self.parse_followup_period(followup_period)
            appointment_date = datetime.now() + delta
            
            # Default appointment time (9:00 AM)
            appointment_time = "09:00 AM"
            
            # Create appointment object
            appointment = {
                'id': self._generate_appointment_id(),
                'patient_name': patient_name,
                'date': appointment_date.strftime('%Y-%m-%d'),
                'time': appointment_time,
                'type': appointment_type,
                'status': 'scheduled',
                'created_at': datetime.now().isoformat()
            }
            
            # Load existing appointments
            appointments = self._load_appointments()
            appointments.append(appointment)
            
            # Save updated appointments
            self._save_appointments(appointments)
            
            logger.info(f"Appointment scheduled: {patient_name} on {appointment['date']}")
            return appointment
        
        except Exception as e:
            logger.error(f"Failed to schedule appointment: {str(e)}")
            return None
    
    def _generate_appointment_id(self):
        """Generate a unique appointment ID"""
        appointments = self._load_appointments()
        if appointments:
            max_id = max([int(a.get('id', 0)) for a in appointments])
            return str(max_id + 1)
        return "1"
    
    def get_appointments_for_patient(self, patient_name):
        """Get all appointments for a patient"""
        try:
            appointments = self._load_appointments()
            return [a for a in appointments if a['patient_name'] == patient_name]
        except Exception as e:
            logger.error(f"Failed to get appointments: {str(e)}")
            return []
    
    def get_upcoming_appointments(self, days=30):
        """Get upcoming appointments within specified days"""
        try:
            appointments = self._load_appointments()
            cutoff_date = datetime.now() + timedelta(days=days)
            
            upcoming = []
            for appt in appointments:
                appt_date = datetime.strptime(appt['date'], '%Y-%m-%d')
                if appt_date <= cutoff_date and appt['status'] == 'scheduled':
                    upcoming.append(appt)
            
            return sorted(upcoming, key=lambda x: x['date'])
        except Exception as e:
            logger.error(f"Failed to get upcoming appointments: {str(e)}")
            return []
    
    def cancel_appointment(self, appointment_id):
        """Cancel an appointment"""
        try:
            appointments = self._load_appointments()
            for appt in appointments:
                if appt['id'] == appointment_id:
                    appt['status'] = 'cancelled'
            
            self._save_appointments(appointments)
            logger.info(f"Appointment cancelled: {appointment_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel appointment: {str(e)}")
            return False