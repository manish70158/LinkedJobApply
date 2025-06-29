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

# Run in background and headless mode for Ubuntu
run_in_background = True if is_linux or running_in_actions else False
safe_mode = True if is_linux or running_in_actions else False

# Run continuously setting
run_non_stop = False               # Set to False for GitHub Actions compatibility

# Browser settings
stealth_mode = False              # Disable stealth mode for better Ubuntu compatibility
disable_extensions = True         # Better performance on Linux
smooth_scroll = False            # Better performance on Linux
keep_screen_awake = True         # Keep system active during long runs

# Close external application tabs
close_tabs = True

# Follow easy applied companies?
follow_companies = False

# Search behavior
alternate_sortby = True
cycle_date_posted = True
stop_date_cycle_at_24hr = True

# Click timing (increased for stability on Linux)
click_gap = 2 if is_linux else 1

# >>>>>>>>>>> Directory Settings <<<<<<<<<<<

# File paths
file_name = "all excels/all_applied_applications_history.csv"
failed_file_name = "all excels/all_failed_applications_history.csv"
logs_folder_path = "logs/"

# Resume paths (Experimental & In Development)
generated_resume_path = "all resumes/"

# AI settings
showAiErrorAlerts = False if is_linux or running_in_actions else True

# Create required directories
for path in [file_name, failed_file_name, logs_folder_path, downloads_path]:
    dir_path = Path(path).parent if '.' in Path(path).name else Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    
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