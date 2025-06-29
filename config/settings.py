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
if running_in_actions:
    downloads_path = '/home/runner/Downloads'
elif is_linux:
    downloads_path = os.path.expanduser('~/Downloads')
else:
    downloads_path = os.path.expanduser('~/Downloads')

# >>>>>>>>>>> LinkedIn Settings <<<<<<<<<<<

# Keep the External Application tabs open?
close_tabs = True                   # Close tabs in headless mode

# Follow easy applied companies
follow_companies = False            

# Run in background and headless mode for GitHub Actions
run_in_background = False          # Set to False to see Chrome running
run_non_stop = False               
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
disable_extensions = True          # Better performance
safe_mode = True                  # Use guest profile for stability
smooth_scroll = False             # Better performance
keep_screen_awake = False         # Prevent sleep during long runs
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