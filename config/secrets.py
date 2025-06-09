'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    24.12.3.10.30
'''


###################################################### CONFIGURE YOUR TOOLS HERE ######################################################


# Login Credentials for LinkedIn (Optional)
username = ""       # Enter your username in the quotes
password = ""           # Enter your password in the quotes


## Artificial Intelligence (Beta Not-Recommended)
# Use AI
use_AI = True                          # True or False, Note: True or False are case-sensitive
'''
Note: Set it as True only if you want to use AI, and If you either have a
1. Local LLM model running on your local machine, with it's APIs exposed. Example softwares to achieve it are:
    a. Ollama - https://ollama.com/
    b. llama.cpp - https://github.com/ggerganov/llama.cpp
    c. LM Studio - https://lmstudio.ai/ (Recommended)
    d. Jan - https://jan.ai/
2. OR you have a valid OpenAI API Key, and money to spare, and you don't mind spending it.
3. OR you have a valid Gemini API key from Google AI Studio.
CHECK THE OPENAI API PIRCES AT THEIR WEBSITE (https://openai.com/api/pricing/). 
'''

##> ------ Yang Li : MARKYangL - Feature ------
# Select AI Provider
ai_provider = "gemini"               # "openai", "deepseek", "ollama", "gemini"
'''
Note: Select your AI provider.
* "openai" - OpenAI API (GPT models)
* "deepseek" - DeepSeek API (DeepSeek models)
* "ollama" - Local Ollama instance
* "gemini" - Google Gemini API
'''

##> ------ Manish Kumar : a.manish1689@gmail.com - Feature ------
# Gemini Configuration
import os
# Try to get API key from environment variable first, fall back to hardcoded value
gemini_api_key = os.environ.get("GEMINI_API_KEY", "")  # Get API key from environment variable
gemini_model = "gemini-2.0-flash"              # Using faster model which may be more reliable
showAiErrorAlerts = False                       # Show error alerts to help with debugging
'''
Note: Gemini API model selection
* "gemini-1.5-pro" - Most capable Gemini model, best for complex tasks (Recommended)
* "gemini-1.5-flash" - Fastest Gemini model, best for simpler tasks
* "gemini-1.0-pro" - Legacy Gemini model

For security, the API key is read from environment variables when available.
When running on GitHub Actions, set the GEMINI_API_KEY secret in your repository settings.
'''
##<

# Your Local LLM url or other AI api url and port
llm_api_url = "http://localhost:11434"  # Ollama's default API endpoint
llm_api_key = ""  # Leave empty for Ollama
llm_model = "llama2:latest"  # Or any other model you have in Ollama
llm_spec = "openai-like"  # Keep this as "openai-like" for Ollama
'''
Note: Currently "openai" and "openai-like" api endpoints are supported.
'''

# # Yor local embedding model name or other AI Embedding model name
# llm_embedding_model = "nomic-embed-text-v1.5"

# Do you want to stream AI output?
stream_output = False                    # Examples: True or False. (False is recommended for performance, True is recommended for user experience!)
'''
Set `stream_output = True` if you want to stream AI output or `stream_output = False` if not.
'''
##




############################################################################################################
'''
THANK YOU for using my tool 😊! Wishing you the best in your job hunt 🙌🏻!

Sharing is caring! If you found this tool helpful, please share it with your peers 🥺. Your support keeps this project alive.

Support my work on <PATREON_LINK>. Together, we can help more job seekers.

As an independent developer, I pour my heart and soul into creating tools like this, driven by the genuine desire to make a positive impact.

Your support, whether through donations big or small or simply spreading the word, means the world to me and helps keep this project alive and thriving.

Gratefully yours 🙏🏻,
Sai Vignesh Golla
'''
############################################################################################################