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
        
        # Create the extraction prompt
        prompt = f"""
        Extract key skills and requirements from the following job description.
        Return a JSON object with keys for:
        - "technical_skills": list of technical skills required
        - "soft_skills": list of soft skills mentioned
        - "experience": years of experience required
        - "education": education requirements
        - "certifications": any certifications mentioned
        
        Job Description:
        {job_description}
        """
        
        # Set up output parser for structured JSON
        json_parser = JsonOutputParser()
        
        # Create a fixing parser to handle JSON errors
        fixing_parser = OutputFixingParser.from_llm(
            parser=json_parser,
            llm=client
        )
        
        # Invoke with the prompt
        response = client.invoke(prompt)
        print_lg("\nLangChain Ollama Raw Response:")
        print_lg(response.content)
        
        # Parse the response to JSON
        try:
            # First try to parse directly
            result = json_parser.parse(response.content)
        except Exception:
            # If direct parsing fails, use the fixing parser
            result = fixing_parser.parse(response.content)
        
        print_lg("\nExtracted Skills (JSON):")
        print_lg(json.dumps(result, indent=2))
        
        return result
    except Exception as e:
        critical_error_log("Error extracting skills with LangChain Ollama!", e)
        print_lg(f"Error details: {str(e)}")
        return {"error": str(e)}

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