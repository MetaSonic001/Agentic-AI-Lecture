import json
from datetime import datetime
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger()

class NotificationService:
    """
    Service for sending notifications (email/SMS)
    Mock implementation that logs notifications
    Can be extended to integrate with Twilio/SMTP
    """
    
    def __init__(self, notifications_file='data/notifications.json'):
        self.notifications_file = notifications_file
        
        # Create data directory
        Path('data').mkdir(exist_ok=True)
        
        # Initialize notifications file
        if not Path(notifications_file).exists():
            self._save_notifications([])
        
        logger.info("Notification Service initialized")
    
    def _load_notifications(self):
        """Load notifications from file"""
        try:
            with open(self.notifications_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load notifications: {str(e)}")
            return []
    
    def _save_notifications(self, notifications):
        """Save notifications to file"""
        try:
            with open(self.notifications_file, 'w') as f:
                json.dump(notifications, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save notifications: {str(e)}")
    
    def _log_notification(self, notification_type, patient_name, message, status='sent'):
        """Log a notification"""
        try:
            notification = {
                'id': self._generate_notification_id(),
                'type': notification_type,
                'patient_name': patient_name,
                'message': message,
                'status': status,
                'timestamp': datetime.now().isoformat()
            }
            
            notifications = self._load_notifications()
            notifications.append(notification)
            self._save_notifications(notifications)
            
            return notification
        except Exception as e:
            logger.error(f"Failed to log notification: {str(e)}")
            return None
    
    def _generate_notification_id(self):
        """Generate a unique notification ID"""
        notifications = self._load_notifications()
        if notifications:
            max_id = max([int(n.get('id', 0)) for n in notifications])
            return str(max_id + 1)
        return "1"
    
    def send_appointment_reminder(self, patient_name, appointment_date, appointment_time):
        """
        Send appointment reminder notification
        
        Args:
            patient_name: Name of the patient
            appointment_date: Date of appointment
            appointment_time: Time of appointment
        
        Returns:
            str: Confirmation message
        """
        try:
            message = f"""
            Dear {patient_name},
            
            This is a reminder for your upcoming appointment:
            Date: {appointment_date}
            Time: {appointment_time}
            
            Please arrive 10 minutes early.
            If you need to reschedule, please contact us.
            
            Best regards,
            Medical Clinic
            """
            
            self._log_notification(
                notification_type='appointment_reminder',
                patient_name=patient_name,
                message=message.strip()
            )
            
            logger.info(f"Appointment reminder sent to {patient_name}")
            return f"Appointment reminder sent for {appointment_date} at {appointment_time}"
        
        except Exception as e:
            logger.error(f"Failed to send appointment reminder: {str(e)}")
            return "Failed to send appointment reminder"
    
    def send_prescription_notification(self, patient_name, prescription):
        """
        Send prescription notification
        
        Args:
            patient_name: Name of the patient
            prescription: List of prescription items
        
        Returns:
            str: Confirmation message
        """
        try:
            # Build prescription list
            med_list = []
            for med in prescription:
                med_info = f"- {med.get('medication', 'N/A')}: {med.get('dosage', 'N/A')}, {med.get('frequency', 'N/A')} for {med.get('duration', 'N/A')}"
                med_list.append(med_info)
            
            medications_text = "\n".join(med_list) if med_list else "See prescription document"
            
            message = f"""
            Dear {patient_name},
            
            Your prescription has been prepared:
            
            {medications_text}
            
            Please follow the instructions carefully.
            Contact us if you have any questions.
            
            Best regards,
            Medical Clinic
            """
            
            self._log_notification(
                notification_type='prescription',
                patient_name=patient_name,
                message=message.strip()
            )
            
            logger.info(f"Prescription notification sent to {patient_name}")
            return f"Prescription details sent to {patient_name}"
        
        except Exception as e:
            logger.error(f"Failed to send prescription notification: {str(e)}")
            return "Failed to send prescription notification"
    
    def send_followup_reminder(self, patient_name, days_until_followup):
        """
        Send follow-up reminder notification
        
        Args:
            patient_name: Name of the patient
            days_until_followup: Number of days until follow-up
        
        Returns:
            str: Confirmation message
        """
        try:
            message = f"""
            Dear {patient_name},
            
            This is a reminder that your follow-up appointment is due in {days_until_followup} days.
            
            Please schedule your appointment if you haven't already.
            
            Best regards,
            Medical Clinic
            """
            
            self._log_notification(
                notification_type='followup_reminder',
                patient_name=patient_name,
                message=message.strip()
            )
            
            logger.info(f"Follow-up reminder sent to {patient_name}")
            return f"Follow-up reminder sent for {days_until_followup} days"
        
        except Exception as e:
            logger.error(f"Failed to send follow-up reminder: {str(e)}")
            return "Failed to send follow-up reminder"
    
    def get_notifications_for_patient(self, patient_name):
        """Get all notifications for a patient"""
        try:
            notifications = self._load_notifications()
            return [n for n in notifications if n['patient_name'] == patient_name]
        except Exception as e:
            logger.error(f"Failed to get notifications: {str(e)}")
            return []
    
    def get_recent_notifications(self, limit=10):
        """Get recent notifications"""
        try:
            notifications = self._load_notifications()
            return sorted(notifications, key=lambda x: x['timestamp'], reverse=True)[:limit]
        except Exception as e:
            logger.error(f"Failed to get recent notifications: {str(e)}")
            return []