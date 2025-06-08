'''
Author:     Manish Kumar
Email:      a.manish1689@gmail.com

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    24.12.29.12.30
'''

from config.secrets import gemini_api_key, gemini_model, showAiErrorAlerts, stream_output
from config.personals import ethnicity, gender, disability_status, veteran_status
from config.questions import *
from config.search import security_clearance, did_masters

from modules.helpers import print_lg, critical_error_log, convert_to_json

from pyautogui import confirm
from typing import Iterator, Literal

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except ImportError:
    print("Google GenerativeAI package not found. Installing...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold

apiCheckInstructions = """
To use Google's Gemini API, you need to:
1. Visit Google AI Studio at https://ai.google.dev/
2. Get an API key
3. Add it to config/secrets.py as gemini_api_key value
"""

def gemini_error_alert(message: str, exception: Exception = None) -> None:
    """
    Shows an alert with Gemini API error message.
    """
    if showAiErrorAlerts:
        error_message = f"{message}\n\n{exception}" if exception else message
        confirm(error_message, "Gemini API Error")

def gemini_create_client() -> genai.GenerativeModel:
    """
    Creates a connection to the Gemini API.
    """
    try:
        if not gemini_api_key:
            raise ValueError("Gemini API key not found in config/secrets.py")
            
        genai.configure(api_key=gemini_api_key)
        
        # Configure safety settings
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        # Create the generative model client
        model = genai.GenerativeModel(
            model_name=gemini_model,
            safety_settings=safety_settings,
            generation_config={
                "temperature": 0.2, 
                "top_p": 0.95,
                "top_k": 40
            }
        )
        
        print_lg(f"Gemini API client created successfully with model {gemini_model}")
        return model
    
    except Exception as e:
        gemini_error_alert(f"Error occurred while connecting to Gemini API. {apiCheckInstructions}", e)
        critical_error_log("Gemini API Connection", e)
        return None

def gemini_extract_skills(client: genai.GenerativeModel, job_description: str) -> dict:
    """
    Function to extract skills from job description using Gemini API.
    """
    try:
        if not client:
            raise ValueError("No Gemini client provided")
            
        prompt = f"""
        Analyze the job description below and extract the following information in a structured JSON format:
        - technical_skills: A list of technical skills required for the job
        - soft_skills: A list of soft skills required for the job
        - experience: Number of years of experience required (as a number, if mentioned)
        - education: List of educational requirements
        - certifications: List of certifications mentioned (if any)
        
        Return only a valid JSON object with these fields.
        
        Job Description:
        {job_description}
        """
        
        response = client.generate_content(prompt)
        
        # Extract and parse JSON from response
        response_text = response.text
        try:
            skills_json = convert_to_json(response_text)
            print_lg("Successfully extracted skills using Gemini API")
            return skills_json
        except Exception as json_err:
            print_lg("Failed to parse Gemini API response as JSON:", json_err)
            return {"error": f"Invalid JSON response from Gemini: {response_text}"}
            
    except Exception as e:
        gemini_error_alert(f"Error occurred while extracting skills from job description. {apiCheckInstructions}", e)
        print_lg("Gemini API Skills Extraction Error:", e)
        return {"error": str(e)}

def gemini_answer_question(
    client: genai.GenerativeModel, 
    question: str, 
    options: list[str] = None, 
    question_type: Literal['text', 'textarea', 'single_select', 'multiple_select'] = 'text',
    job_description: str = None, 
    about_company: str = None, 
    user_information_all: str = None,
    stream: bool = stream_output
) -> str:
    """
    Function to answer job application questions using Gemini API.
    """
    try:
        if not client:
            raise ValueError("No Gemini client provided")
            
        # Construct the prompt based on question type and available context
        base_prompt = f"""
        You are an AI assistant helping with a job application question. 
        
        Question: {question}
        Question type: {question_type}
        """
        
        if options:
            base_prompt += f"\nOptions: {options}"
            
        if job_description:
            base_prompt += f"\n\nJob Description:\n{job_description}"
            
        if about_company:
            base_prompt += f"\n\nAbout the Company:\n{about_company}"
            
        if user_information_all:
            base_prompt += f"\n\nUser Information:\n{user_information_all}"
            
        base_prompt += """
        
        Answer the question professionally and appropriately for a job application. 
        Keep responses brief but complete.
        If it's a text field, provide a short answer.
        If it's a textarea, provide a more detailed response (2-3 paragraphs).
        If it's a selection, just return the best option from the provided options.
        
        Your answer:
        """
        
        # Generate response
        response = client.generate_content(base_prompt)
        
        # Extract answer
        answer = response.text.strip()
        
        print_lg(f"Gemini generated answer for question: {question}")
        return answer
        
    except Exception as e:
        gemini_error_alert(f"Error occurred while answering job application question. {apiCheckInstructions}", e)
        print_lg("Gemini Question Answering Error:", e)
        return ""

def gemini_close_client(client: genai.GenerativeModel) -> None:
    """
    Function to close Gemini client connection (not needed for Gemini API but included for compatibility).
    """
    try:
        print_lg("Closing Gemini API client - Note: Gemini API doesn't require explicit closure")
        # No explicit closure needed for Gemini API
    except Exception as e:
        gemini_error_alert("Error occurred while closing Gemini API client.", e)