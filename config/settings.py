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

# Detect environment
running_in_actions = os.environ.get('GITHUB_ACTIONS') == 'true' or os.environ.get('CI') == 'true'
is_linux = platform.system().lower() == 'linux'

# Set paths based on environment
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Set downloads path based on environment
if running_in_actions:
    downloads_path = os.path.join(current_dir, 'downloads')
elif is_linux:
    downloads_path = os.path.expanduser('~/Downloads')
    if not os.path.exists(downloads_path):
        downloads_path = os.path.join(current_dir, 'downloads')
else:
    downloads_path = os.path.expanduser('~/Downloads')

# Ensure downloads directory exists
os.makedirs(downloads_path, exist_ok=True)

# >>>>>>>>>>> LinkedIn Settings <<<<<<<<<<<

# Keep the External Application tabs open?
close_tabs = True                   # Close tabs in headless mode

# Follow easy applied companies
follow_companies = False            

# Run in background and headless mode
run_in_background = True if is_linux or running_in_actions else False
safe_mode = True if is_linux or running_in_actions else False
alternate_sortby = True             
cycle_date_posted = True            
stop_date_cycle_at_24hr = True      

# >>>>>>>>>>> Global Settings <<<<<<<<<<<

# Directory and file paths
file_name = "all excels/all_applied_applications_history.csv"
failed_file_name = "all excels/all_failed_applications_history.csv"
logs_folder_path = "logs/"

# Minimal delay for stability
click_gap = 1                      # Wait time between clicks in seconds

# Chrome configuration
disable_extensions = True          # Better performance on Linux
stealth_mode = False              # Disable stealth mode for stability
smooth_scroll = False if is_linux else True  # Better performance on Linux
keep_screen_awake = True         # Prevent sleep during long runs

# AI-related settings
showAiErrorAlerts = False         # Disable alerts in headless mode

# >>>>>>>>>>> RESUME GENERATOR (Experimental & In Development) <<<<<<<<<<<
generated_resume_path = "all resumes/" # (In Development)

# Create required directories
for path in [file_name, failed_file_name, logs_folder_path, downloads_path]:
    os.makedirs(os.path.dirname(path) if '.' in path.split('/')[-1] else path, exist_ok=True)
    
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