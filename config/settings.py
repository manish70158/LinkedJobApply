'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    24.12.29.12.30
'''


###################################################### CONFIGURE YOUR BOT HERE ######################################################

# >>>>>>>>>>> Environment Settings <<<<<<<<<<<
import os
import platform
from pathlib import Path

# Detect environment
running_in_actions = os.environ.get('GITHUB_ACTIONS') == 'true' or os.environ.get('CI') == 'true'
is_linux = platform.system().lower() == 'linux'

# Set absolute paths based on environment
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Set downloads path based on environment
if running_in_actions:
    downloads_path = os.path.join(current_dir, 'downloads')
elif is_linux:
    downloads_path = os.path.expanduser('~/Downloads')
else:
    downloads_path = os.path.expanduser('~/Downloads')

# Safely create downloads directory if it doesn't exist
try:
    Path(downloads_path).mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create downloads directory: {e}")
    # Fall back to current directory if we can't create downloads directory
    downloads_path = os.path.join(current_dir, 'downloads')
    Path(downloads_path).mkdir(parents=True, exist_ok=True)

# >>>>>>>>>>> LinkedIn Settings <<<<<<<<<<<

# Keep the External Application tabs open?
close_tabs = True                   # Close tabs in headless mode

# Follow easy applied companies
follow_companies = False            

# Run in background and headless mode for GitHub Actions
run_in_background = True if running_in_actions else False
safe_mode = True if running_in_actions else False
stealth_mode = False
disable_extensions = True if running_in_actions else False

# >>>>>>>>>>> Global Settings <<<<<<<<<<<

# Directory and file paths
file_name = "all excels/all_applied_applications_history.csv"
failed_file_name = "all excels/all_failed_applications_history.csv"
logs_folder_path = "logs/"

# Minimal delay for stability
click_gap = 1                      # Wait time between clicks in seconds

# Chrome configuration
disable_extensions = False          # Better performance
safe_mode = False                  # Use guest profile for stability
smooth_scroll = True              # Better performance
keep_screen_awake = True         # Prevent sleep during long runs
stealth_mode = False             # Disable stealth mode for stability

# AI-related settings
showAiErrorAlerts = False         # Disable alerts in headless mode

# >>>>>>>>>>> RESUME GENERATOR (Experimental & In Development) <<<<<<<<<<<
generated_resume_path = "all resumes/" # (In Development)





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