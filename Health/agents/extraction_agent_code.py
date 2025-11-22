import json
import os
from datetime import datetime
from crewai import Agent, Task, Crew
from langchain_groq import ChatGroq
from utils.logger import setup_logger

logger = setup_logger()

class ExtractionAgent:
    """Agent responsible for extracting structured information from doctor's notes"""
    
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0,
            model_name="mixtral-8x7b-32768",
            api_key=os.getenv("GROQ_API_KEY")
        )
        logger.info("Extraction Agent initialized")
    
    def create_agent(self):
        """Create the extraction agent"""
        return Agent(
            role="Medical Information Extractor",
            goal="Extract structured medical information from doctor's notes including diagnosis, vitals, medications, and follow-up requirements",
            backstory="""You are an expert medical information extraction specialist with years of experience 
            in parsing clinical notes and converting them into structured data. You understand medical terminology, 
            vital signs, medication dosages, and appointment scheduling requirements.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def create_extraction_task(self, agent, note, patient_name, patient_age):
        """Create the extraction task"""
        return Task(
            description=f"""
            Extract structured information from the following doctor's note:
            
            Patient Name: {patient_name}
            Patient Age: {patient_age}
            Doctor's Note: {note}
            
            Extract and structure the following information:
            1. Patient Information (name, age)
            2. Diagnosis (primary condition identified)
            3. Vital Signs (temperature, blood pressure, heart rate, etc. if mentioned)
            4. Symptoms (list of symptoms mentioned)
            5. Prescription (medications with dosage and duration)
            6. Follow-up (when the next appointment should be scheduled)
            7. Appointment Type (routine, urgent, specialist referral, etc.)
            
            Return ONLY a valid JSON object with this exact structure:
            {{
                "patient": {{
                    "name": "string",
                    "age": number
                }},
                "diagnosis": "string",
                "symptoms": ["string"],
                "vitals": {{
                    "temperature": "string",
                    "blood_pressure": "string",
                    "heart_rate": "string",
                    "other": "string"
                }},
                "prescription": [
                    {{
                        "medication": "string",
                        "dosage": "string",
                        "frequency": "string",
                        "duration": "string"
                    }}
                ],
                "followup": "string (e.g., '7 days', '2 weeks', '1 month')",
                "appointment_type": "string (routine/urgent/specialist)"
            }}
            
            If any information is not mentioned in the note, use "Not mentioned" or empty array/object.
            """,
            agent=agent,
            expected_output="A valid JSON object containing all extracted medical information"
        )
    
    def extract(self, note, patient_name, patient_age):
        """Execute the extraction process"""
        logger.info(f"Starting extraction for patient: {patient_name}")
        
        try:
            # Create agent and task
            agent = self.create_agent()
            task = self.create_extraction_task(agent, note, patient_name, patient_age)
            
            # Create and run crew
            crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=True
            )
            
            result = crew.kickoff()
            
            # Parse the result
            result_str = str(result)
            
            # Try to extract JSON from the result
            try:
                # Find JSON in the response
                start_idx = result_str.find('{')
                end_idx = result_str.rfind('}') + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = result_str[start_idx:end_idx]
                    extracted_data = json.loads(json_str)
                else:
                    # If no JSON found, create a basic structure
                    extracted_data = self._create_fallback_structure(note, patient_name, patient_age)
            
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from result, using fallback")
                extracted_data = self._create_fallback_structure(note, patient_name, patient_age)
            
            # Ensure patient info is correct
            extracted_data['patient'] = {
                'name': patient_name,
                'age': patient_age
            }
            
            logger.info("Extraction completed successfully")
            return extracted_data
        
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise
    
    def _create_fallback_structure(self, note, patient_name, patient_age):
        """Create a fallback structure when JSON parsing fails"""
        return {
            "patient": {
                "name": patient_name,
                "age": patient_age
            },
            "diagnosis": "To be determined",
            "symptoms": ["See note"],
            "vitals": {
                "temperature": "Not mentioned",
                "blood_pressure": "Not mentioned",
                "heart_rate": "Not mentioned",
                "other": note[:100]
            },
            "prescription": [],
            "followup": "7 days",
            "appointment_type": "routine"
        }