##> ------ Yang Li : MARKYangL - Feature ------
from config.secrets import *
from config.settings import showAiErrorAlerts
from modules.helpers import print_lg, critical_error_log, convert_to_json
from modules.ai.prompts import *

# Import LangChain components
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from langchain_core.prompts import ChatPromptTemplate
from typing import Iterator, Literal, Dict, Any, List, Optional
import json

# Create a reusable function to get LangChain Ollama client
def get_langchain_ollama(
    model: str = llm_model, 
    temperature: float = 0.0,
    max_tokens: int = 2000
) -> ChatOllama:
    """
    Creates a LangChain Ollama client
    * Returns a configured LangChain ChatOllama instance
    """
    try:
        print_lg(f"Creating LangChain Ollama client with model {model}...")
        
        if not use_AI:
            raise ValueError("AI is not enabled! Please enable it by setting `use_AI = True` in `secrets.py` in `config` folder.")
        
        # Extract base URL from configured URL or use default
        base_url = llm_api_url
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        
        # Remove /v1 if present (different format between OpenAI and LangChain)
        if '/v1' in base_url:
            base_url = base_url.split('/v1')[0]
        
        # Create the LangChain Ollama client
        llm = ChatOllama(
            base_url=base_url,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        print_lg("---- SUCCESSFULLY CREATED LANGCHAIN OLLAMA CLIENT! ----")
        print_lg(f"Using API URL: {base_url}")
        print_lg(f"Using Model: {model}")
        print_lg("---------------------------------------------")
        
        return llm
    except Exception as e:
        error_message = f"Error creating LangChain Ollama client: {str(e)}"
        critical_error_log(error_message, e)
        if showAiErrorAlerts:
            print_lg(f"ERROR: {error_message}")
            print_lg("Continue with process, but AI features may not work.")
        return None

# For backward compatibility with existing code
def ollama_create_client() -> Any:
    """
    Creates a LangChain Ollama client (backward compatibility function)
    """
    return get_langchain_ollama()

def ollama_extract_skills(client: ChatOllama, job_description: str, stream: bool = stream_output) -> Dict[str, Any]:
    '''
    Function to extract skills from job description using LangChain Ollama.
    '''
    try:
        print_lg("Extracting skills from job description using LangChain...")
        
        # Create the extraction prompt with explicit JSON format instructions
        prompt = f"""
        Extract key skills and requirements from the following job description.
        Return ONLY a valid JSON object with NO additional text or explanation, with keys for:
        - "technical_skills": list of technical skills required
        - "soft_skills": list of soft skills mentioned
        - "experience": years of experience required (as a number only)
        - "education": education requirements
        - "certifications": any certifications mentioned
        
        Job Description:
        {job_description}
        
        Format your response as valid JSON only! No additional text, explanations, or apologies.
        """
        
        # Invoke with the prompt
        response = client.invoke(prompt)
        print_lg("\nLangChain Ollama Raw Response:")
        print_lg(response.content)
        
        # Parse the response to JSON
        try:
            # Extract just the JSON part from the response
            json_content = extract_json_from_text(response.content)
            # Parse the extracted JSON
            if json_content:
                result = json.loads(json_content)
                print_lg("\nExtracted Skills (JSON):")
                print_lg(json.dumps(result, indent=2))
                return result
            else:
                raise ValueError("No valid JSON found in response")
        except Exception as json_err:
            print_lg(f"Failed to parse JSON directly: {str(json_err)}")
            
            # Try a more lenient approach - create a basic structure if parsing fails
            skills_json = {
                "technical_skills": extract_skills_from_text(response.content, "technical"),
                "soft_skills": extract_skills_from_text(response.content, "soft"),
                "experience": extract_experience_from_text(response.content),
                "education": extract_education_from_text(response.content),
                "certifications": extract_certs_from_text(response.content)
            }
            return skills_json
            
    except Exception as e:
        critical_error_log("Error extracting skills with LangChain Ollama!", e)
        print_lg(f"Error details: {str(e)}")
        return {"error": str(e)}

def extract_json_from_text(text: str) -> str:
    """
    Extract JSON string from text that may contain non-JSON content
    """
    # Look for JSON content between curly braces
    import re
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        return json_match.group(0)
    return None

def extract_skills_from_text(text: str, skill_type: str) -> List[str]:
    """
    Extract skills from text when JSON parsing fails
    """
    skills = []
    lines = text.lower().split('\n')
    in_section = False
    
    section_markers = {
        "technical": ["technical skills", "tech skills", "hard skills"],
        "soft": ["soft skills", "interpersonal skills"]
    }
    
    markers = section_markers.get(skill_type, [])
    
    for line in lines:
        # Check if we're entering a relevant section
        if any(marker in line.lower() for marker in markers):
            in_section = True
            continue
        
        # Check if we're exiting the section
        if in_section and any(marker in line.lower() for marker in ["experience", "education", "certification"]):
            in_section = False
        
        # Extract skills from lines within the section
        if in_section and (":" in line or "-" in line or "•" in line or "*" in line):
            # Extract the skill after the delimiter
            skill = line.split(":", 1)[-1].split("-", 1)[-1].split("•", 1)[-1].split("*", 1)[-1].strip()
            if skill and len(skill) > 1 and not skill.startswith(('http', 'www')):
                skills.append(skill)
    
    # If no skills found using section detection, try to extract anything that looks like a skill
    if not skills and skill_type == "technical":
        potential_tech_skills = re.findall(r'\b(Java|Python|React|Docker|AWS|Azure|SQL|JavaScript|Node\.js|C#|\.NET|Angular|MongoDB|Kubernetes|Spring|Git|REST|API|HTML|CSS)\b', text)
        skills = list(set(potential_tech_skills))
    
    return skills

def extract_experience_from_text(text: str) -> int:
    """
    Extract years of experience from text
    """
    import re
    # Look for patterns like "5+ years", "3-5 years", "at least 5 years"
    exp_patterns = [
        r'(\d+)\+?\s*(?:to\s*\d+)?\s*years?',
        r'(\d+)\s*-\s*\d+\s*years?',
        r'at least\s*(\d+)\s*years?',
        r'minimum\s*(?:of\s*)?(\d+)\s*years?'
    ]
    
    for pattern in exp_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    
    return 0  # Default if no experience requirement found

def extract_education_from_text(text: str) -> List[str]:
    """
    Extract education requirements from text
    """
    education = []
    if "bachelor" in text.lower() or "b.s." in text.lower() or "b.a." in text.lower():
        education.append("Bachelor's degree")
    if "master" in text.lower() or "m.s." in text.lower() or "m.a." in text.lower():
        education.append("Master's degree")
    if "phd" in text.lower() or "doctorate" in text.lower():
        education.append("PhD")
    return education

def extract_certs_from_text(text: str) -> List[str]:
    """
    Extract certifications from text
    """
    cert_keywords = ["certification", "certified", "certificate"]
    certs = []
    lines = text.split('\n')
    
    for line in lines:
        if any(keyword in line.lower() for keyword in cert_keywords):
            cert = line.strip()
            if cert:
                certs.append(cert)
    
    return certs

def ollama_completion(
    client: ChatOllama, 
    messages: List[Dict[str, str]], 
    response_format: Optional[Dict] = None, 
    temperature: float = 0.0, 
    stream: bool = stream_output
) -> str:
    '''
    Completes a chat using LangChain Ollama and formats the results.
    '''
    if not client: 
        raise ValueError("LangChain Ollama client is not available!")

    try:
        # Convert OpenAI-style messages to LangChain format
        langchain_messages = []
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "system":
                langchain_messages.append(SystemMessage(content=msg["content"]))
            # Add assistant role if needed
        
        # If no messages provided, raise error
        if not langchain_messages:
            raise ValueError("No messages provided for completion")
        
        print_lg(f"Calling LangChain Ollama for completion...")
        print_lg(f"Message count: {len(messages)}")
        
        # Set temperature if different from default
        if temperature != 0.0:
            client.temperature = temperature
        
        # For streaming mode
        if stream:
            print_lg("--STREAMING STARTED")
            result = ""
            for chunk in client.stream(langchain_messages):
                if chunk.content:
                    result += chunk.content
                    print_lg(chunk.content, end="", flush=True)
            print_lg("\n--STREAMING COMPLETE")
        else:
            # For non-streaming mode
            completion = client.invoke(langchain_messages)
            result = completion.content
        
        # Handle JSON response format if needed
        if response_format and response_format.get("type") == "json_object":
            try:
                # Try to parse as JSON
                json_result = json.loads(result)
                result = json_result
            except json.JSONDecodeError:
                # If not valid JSON, use a JSON parser to fix and parse it
                json_parser = JsonOutputParser()
                fixing_parser = OutputFixingParser.from_llm(
                    parser=json_parser,
                    llm=client
                )
                result = fixing_parser.parse(result)
        
        print_lg("\nLangChain Ollama Answer:")
        if isinstance(result, dict):
            print_lg(json.dumps(result, indent=2))
        else:
            print_lg(result)
            
        return result
    except Exception as e:
        error_message = f"LangChain Ollama error: {str(e)}"
        print_lg(f"Full error details: {e.__class__.__name__}: {str(e)}")
        
        # Add hints for common errors
        if "Connection" in str(e):
            print_lg("This might be a network issue. Check your internet connection.")
            print_lg("If you're behind a firewall or proxy, make sure it allows connections to Ollama API.")
        
        raise ValueError(error_message)

def ollama_answer_question(
    client: ChatOllama, 
    question: str, 
    options: List[str] = None, 
    question_type: Literal['text', 'textarea', 'single_select', 'multiple_select'] = 'text', 
    job_description: str = None, 
    about_company: str = None, 
    user_information_all: str = None,
    stream: bool = stream_output
) -> str:
    '''
    Function to answer a question using LangChain Ollama.
    '''
    try:
        print_lg(f"Answering question using LangChain Ollama: {question}")
        
        # Prepare user information
        user_info = user_information_all or ""
        
        # Prepare prompt based on question type
        prompt = ai_answer_prompt.format(user_info, question)
        
        # Add options to the prompt if available
        if options and (question_type in ['single_select', 'multiple_select']):
            options_str = "OPTIONS:\n" + "\n".join([f"- {option}" for option in options])
            prompt += f"\n\n{options_str}"
            
            if question_type == 'single_select':
                prompt += "\n\nPlease select exactly ONE option from the list above."
            else:
                prompt += "\n\nYou may select MULTIPLE options from the list above if appropriate."
        
        # Add job details for context if available
        if job_description:
            prompt += f"\n\nJOB DESCRIPTION:\n{job_description}"
        
        if about_company:
            prompt += f"\n\nABOUT COMPANY:\n{about_company}"
        
        # Adjust temperature for more natural responses
        client.temperature = 0.1
        
        # Get response from LangChain Ollama
        if stream:
            print_lg("--STREAMING STARTED")
            result = ""
            for chunk in client.stream(prompt):
                if chunk.content:
                    result += chunk.content
                    print_lg(chunk.content, end="", flush=True)
            print_lg("\n--STREAMING COMPLETE")
        else:
            response = client.invoke(prompt)
            result = response.content
            
        print_lg("\nQuestion Answer:")
        print_lg(result)
        
        return result
    except Exception as e:
        critical_error_log("Error answering question with LangChain Ollama!", e)
        print_lg(f"Error details: {str(e)}")
        return f"Error: {str(e)}"

# Remove the initial test code that was at the top of the file
##<