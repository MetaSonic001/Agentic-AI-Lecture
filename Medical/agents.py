"""
Multi-Agent Medical Analysis System
Handles all agent logic and coordination
"""

import os
from agno.agent import Agent
from agno.models.groq import Groq


class MedicalAgentSystem:
    """Manages multiple specialized medical AI agents"""
    
    def __init__(self, api_key):
        """Initialize the agent system with Groq API key"""
        self.api_key = api_key
        os.environ['GROQ_API_KEY'] = api_key
        # Create a Groq model/client instance and reuse for all agents
        # Use the Groq model id expected by the system
        try:
            self.llm = Groq(id="llama-3.1-8b-instant", api_key=api_key)
        except TypeError:
            # Older/newer Groq APIs may accept api_key as first arg
            self.llm = Groq(api_key=api_key)
        
        # Initialize agents
        self.diagnostic_agent = self._create_diagnostic_agent()
        self.specialist_agent = self._create_specialist_agent()
        self.coordinator_agent = self._create_coordinator_agent()
    
    def _create_diagnostic_agent(self):
        """Creates agent for initial diagnosis and symptom analysis"""
        return Agent(
            name="Dr. Diagnostic",
            role="Primary Diagnostic Physician",
            instructions=[
                "Analyze medical reports and symptoms thoroughly",
                "Identify key concerns and potential diagnoses",
                "Flag urgent issues that need immediate attention",
                "Be concise and specific with medical terminology",
                "Focus on pattern recognition in symptoms",
                "Consider vital signs and their implications",
                "Identify any life-threatening conditions first"
            ],
            model=self.llm
        )
    
    def _create_specialist_agent(self):
        """Creates specialist agent for detailed analysis"""
        return Agent(
            name="Dr. Specialist",
            role="Medical Specialist Consultant",
            instructions=[
                "Provide specialized medical insights based on findings",
                "Suggest specific diagnostic tests or investigations needed",
                "Consider rare conditions and potential complications",
                "Recommend evidence-based treatment approaches",
                "Note any drug interactions or contraindications",
                "Consider differential diagnoses",
                "Identify specialists that should be consulted"
            ],
            model=self.llm
        )
    
    def _create_coordinator_agent(self):
        """Creates coordinator agent for synthesis"""
        return Agent(
            name="Dr. Coordinator",
            role="Medical Case Coordinator",
            instructions=[
                "Synthesize findings from diagnostic and specialist agents",
                "Create clear, actionable medical recommendations",
                "Prioritize next steps for patient care with timelines",
                "Ensure nothing critical is missed from other agents",
                "Provide patient-friendly summary without medical jargon",
                "Create a cohesive care plan",
                "Highlight follow-up requirements"
            ],
            model=self.llm
        )
    
    def analyze_report(self, medical_report, log_callback=None):
        """
        Run multi-agent analysis on a medical report
        
        Args:
            medical_report (str): The medical report text to analyze
            log_callback (callable): Optional callback function for logging (agent_name, event)
        
        Returns:
            dict: Analysis results from all agents
        """
        results = {}
        
        # Helper function for logging
        def log(agent_name, event):
            if log_callback:
                log_callback(agent_name, event)
        
        try:
            # Step 1: Diagnostic Agent Analysis
            log("System", "🔴 Initializing Dr. Diagnostic...")
            log("Dr. Diagnostic", "Reviewing medical report and analyzing symptoms...")
            
            diagnostic_prompt = f"""Analyze this medical report and provide:

1. **Primary Symptoms & Findings**: List the key symptoms and clinical findings
2. **Initial Diagnostic Impression**: What conditions are most likely based on the presentation?
3. **Urgent Red Flags**: Any critical issues requiring immediate attention?
4. **Vital Signs Assessment**: Analysis of vital signs and their significance

Medical Report:
{medical_report}

Provide a structured, concise analysis."""
            
            diagnostic_response = self.diagnostic_agent.run(diagnostic_prompt)
            results['diagnostic'] = diagnostic_response.content
            log("Dr. Diagnostic", "✅ Primary analysis complete")
            
            # Step 2: Specialist Analysis
            log("System", "🔵 Consulting Dr. Specialist...")
            log("Dr. Specialist", "Providing specialized consultation and recommendations...")
            
            specialist_prompt = f"""Based on this medical report and the initial diagnostic findings, provide specialist-level consultation:

**Medical Report:**
{medical_report}

**Initial Diagnostic Findings:**
{results['diagnostic']}

Please provide:

1. **Specialized Medical Insights**: Deeper analysis from a specialist perspective
2. **Recommended Investigations**: Specific tests, imaging, or labs needed
3. **Differential Diagnoses**: Other conditions to rule out
4. **Treatment Considerations**: Evidence-based treatment options and approaches
5. **Risk Factors & Complications**: What to monitor and potential complications

Be specific and actionable."""
            
            specialist_response = self.specialist_agent.run(specialist_prompt)
            results['specialist'] = specialist_response.content
            log("Dr. Specialist", "✅ Specialist consultation complete")
            
            # Step 3: Coordinator Synthesis
            log("System", "🟢 Dr. Coordinator synthesizing findings...")
            log("Dr. Coordinator", "Creating unified care plan from all analyses...")
            
            coordinator_prompt = f"""Synthesize the following analyses into a comprehensive, actionable care plan:

**Original Medical Report:**
{medical_report}

**Diagnostic Analysis (Dr. Diagnostic):**
{results['diagnostic']}

**Specialist Consultation (Dr. Specialist):**
{results['specialist']}

Create a unified assessment that includes:

1. **Summary Assessment**: Brief overview of the patient's condition
2. **Priority Action Items**: Immediate steps needed (with urgency levels)
3. **Recommended Care Plan**: Short-term and long-term management
4. **Follow-up Requirements**: When and what type of follow-ups needed
5. **Patient-Friendly Explanation**: Simple language summary for patient understanding

Ensure all critical points from both agents are included and nothing is missed."""
            
            coordinator_response = self.coordinator_agent.run(coordinator_prompt)
            results['coordinator'] = coordinator_response.content
            log("Dr. Coordinator", "✅ Synthesis and care plan complete")
            
            log("System", "🎉 Multi-agent analysis successfully completed!")
            
        except Exception as e:
            log("System", f"❌ Error during analysis: {str(e)}")
            raise
        
        return results
    
    def get_agent_info(self):
        """Returns information about all agents in the system"""
        return {
            "diagnostic": {
                "name": "Dr. Diagnostic",
                "role": "Primary Diagnostic Physician",
                "focus": "Initial symptom analysis and diagnosis"
            },
            "specialist": {
                "name": "Dr. Specialist",
                "role": "Medical Specialist Consultant",
                "focus": "Detailed investigation and treatment planning"
            },
            "coordinator": {
                "name": "Dr. Coordinator",
                "role": "Medical Case Coordinator",
                "focus": "Synthesis and comprehensive care planning"
            }
        }


# Example usage (for testing)
if __name__ == "__main__":
    # This will only run if you execute agents.py directly
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("Error: GROQ_API_KEY not found in .env file")
        exit(1)
    
    # Sample test
    system = MedicalAgentSystem(api_key)
    
    test_report = """Patient: 58-year-old male
Chief Complaint: Chest pain
Vitals: BP 150/95, HR 98
Labs: Troponin pending"""
    
    def test_logger(agent, event):
        print(f"[{agent}] {event}")
    
    print("Testing agent system...")
    results = system.analyze_report(test_report, test_logger)
    print("\n=== Results ===")
    print(f"Diagnostic: {len(results['diagnostic'])} chars")
    print(f"Specialist: {len(results['specialist'])} chars")
    print(f"Coordinator: {len(results['coordinator'])} chars")
