import google.generativeai as genai
import os

# Set proxy environment variables
# os.environ["HTTP_PROXY"] = "http://ii747.wip.uhc.com:8080"
# os.environ["HTTPS_PROXY"] = "http://ii747.wip.uhc.com:8080"

# Import your API key from secrets.py
from config.secrets import gemini_api_key, gemini_model

def test_gemini_connection():
    print("Testing Gemini API connection...")
    print(f"Using model: {gemini_model}")
    
    try:
        # Configure the Gemini API
        genai.configure(api_key=gemini_api_key)
        
        # Create a model instance
        model = genai.GenerativeModel(model_name=gemini_model)
        
        # Try a simple generation
        response = model.generate_content("Say hello and confirm that the API connection is working.")
        
        print("\nAPI Response:")
        print(response.text)
        print("\nAPI connection successful!")
        return True
        
    except Exception as e:
        print(f"\nAPI connection failed with error: {e}")
        return False

# Alternative approach using specific model version
def test_alternative_connection():
    print("Testing alternative Gemini API connection...")
    
    try:
        # Configure the API
        genai.configure(api_key=gemini_api_key)
        
        # Create a model instance with specific model version
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        
        # Generate content
        response = model.generate_content("Explain how AI works in a few words")
        
        print("\nAlternative API Response:")
        print(response.text)
        print("\nAlternative API connection successful!")
        return True
        
    except Exception as e:
        print(f"\nAlternative API connection failed with error: {e}")
        return False

if __name__ == "__main__":
    print("Using proxy settings:")
    print(f"HTTP_PROXY: {os.environ.get('HTTP_PROXY')}")
    print(f"HTTPS_PROXY: {os.environ.get('HTTPS_PROXY')}")
    print()
    
    test_gemini_connection()
    print("\n" + "-"*50 + "\n")
    test_alternative_connection()