'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    24.12.29.12.30
'''

import os
import subprocess
import requests
from modules.helpers import make_directories
from config.settings import (
    run_in_background, stealth_mode, disable_extensions, safe_mode, 
    file_name, failed_file_name, logs_folder_path, generated_resume_path,
    running_in_actions, downloads_path
)
from config.questions import default_resume_path
if stealth_mode:
    import undetected_chromedriver as uc
else: 
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from modules.helpers import find_default_profile_directory, critical_error_log, print_lg

def get_chrome_version():
    try:
        # Try different commands for different platforms
        commands = [
            ['google-chrome', '--version'],
            ['chrome', '--version'],
            ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'],
            ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version']
        ]
        for cmd in commands:
            try:
                version = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
                version = version.decode().strip().split()[-1]  # Get last word
                major_version = version.split('.')[0]
                return major_version, version
            except:
                continue
        return None, None
    except:
        return None, None

def get_compatible_chromedriver_version(chrome_major_version):
    try:
        # Try Chrome for Testing first
        url = f"https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_{chrome_major_version}"
        response = requests.get(url)
        if response.status_code == 200 and not "Error" in response.text:
            return response.text.strip(), True  # Second value indicates if it's Chrome for Testing
            
        # Fall back to regular ChromeDriver
        url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{chrome_major_version}"
        response = requests.get(url)
        if response.status_code == 200 and not "Error" in response.text:
            return response.text.strip(), False
            
        # Try previous versions
        for version in range(int(chrome_major_version)-1, int(chrome_major_version)-5, -1):
            url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{version}"
            response = requests.get(url)
            if response.status_code == 200 and not "Error" in response.text:
                return response.text.strip(), False
                
        # If still not found, get latest stable version
        url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
        response = requests.get(url)
        if response.status_code == 200:
            return response.text.strip(), False
    except:
        pass
    return None, False

try:
    # Check for existing Chrome instances
    lock_file = os.path.join(os.path.expanduser('~'), '.chrome_lock')
    if os.path.exists(lock_file):
        try:
            os.remove(lock_file)
        except:
            raise Exception("Chrome appears to be already running. Please close all Chrome windows and try again.")
    
    # Create lock file
    with open(lock_file, 'w') as f:
        f.write(str(os.getpid()))

    make_directories([file_name, failed_file_name, logs_folder_path+"/screenshots", default_resume_path, generated_resume_path+"/temp", downloads_path])

    # Get Chrome version and compatible chromedriver
    chrome_major_version, chrome_full_version = get_chrome_version()
    if chrome_major_version:
        print_lg(f"Detected Chrome version: {chrome_full_version} (Major: {chrome_major_version})")
        chromedriver_version, is_chrome_for_testing = get_compatible_chromedriver_version(chrome_major_version)
        if chromedriver_version:
            print_lg(f"Using {'Chrome for Testing' if is_chrome_for_testing else 'ChromeDriver'} version: {chromedriver_version}")
            os.environ["CHROMEDRIVER_VERSION"] = chromedriver_version
            
            # Download and install correct chromedriver if using Chrome for Testing
            if is_chrome_for_testing:
                try:
                    driver_url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{chromedriver_version}/linux64/chromedriver-linux64.zip"
                    driver_zip = "chromedriver.zip"
                    print_lg(f"Downloading ChromeDriver from: {driver_url}")
                    r = requests.get(driver_url)
                    with open(driver_zip, 'wb') as f:
                        f.write(r.content)
                    os.system(f"unzip -o {driver_zip} && sudo mv chromedriver-linux64/chromedriver /usr/local/bin/ && sudo chmod +x /usr/local/bin/chromedriver")
                    os.remove(driver_zip)
                except Exception as e:
                    print_lg(f"Error downloading ChromeDriver: {e}")

    # Set up WebDriver with Chrome Profile
    options = uc.ChromeOptions() if stealth_mode else Options()
    
    # Configure Chrome for headless/background operation
    if run_in_background or running_in_actions:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        if not stealth_mode:
            options.add_argument("--remote-debugging-port=9222")
    
    if disable_extensions:
        options.add_argument("--disable-extensions")
    
    # Set downloads path and other preferences
    prefs = {
        "download.default_directory": downloads_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    
    # Apply preferences based on driver type
    if stealth_mode:
        options.add_argument(f"--user-data-dir={os.path.expanduser('~')}/chrome-profile")
    else:
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

    print_lg("IF YOU HAVE MORE THAN 10 TABS OPENED, PLEASE CLOSE OR BOOKMARK THEM! Or it's highly likely that application will just open browser and not do anything!")
    if safe_mode or running_in_actions: 
        print_lg("SAFE MODE: Will login with a guest profile, browsing history will not be saved in the browser!")
    else:
        profile_dir = find_default_profile_directory()
        if profile_dir and not stealth_mode: 
            options.add_argument(f"--user-data-dir={profile_dir}")
        else: 
            print_lg("Default profile directory not found. Logging in with a guest profile, Web history will not be saved!")
    
    if stealth_mode:
        print_lg("Using undetected-chromedriver mode...")
        driver = uc.Chrome(options=options)
    else:
        print_lg("Using standard selenium webdriver...")
        if is_chrome_for_testing:
            service = Service(executable_path='/usr/local/bin/chromedriver')
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
    
    driver.maximize_window()
    wait = WebDriverWait(driver, 5)
    actions = ActionChains(driver)

except Exception as e:
    # Remove lock file on error
    try:
        os.remove(lock_file)
    except:
        pass
        
    msg = 'Seems like either... \n\n1. Chrome is already running. \nA. Close all Chrome windows and try again. \n\n2. Google Chrome or Chromedriver is out dated. \nA. Update browser and Chromedriver (You can run "windows-setup.bat" in /setup folder for Windows PC to update Chromedriver)! \n\n3. If error occurred when using "stealth_mode", try reinstalling undetected-chromedriver. \nA. Open a terminal and use commands "pip uninstall undetected-chromedriver" and "pip install undetected-chromedriver". \n\n\nIf issue persists, try Safe Mode. Set, safe_mode = True in config.py \n\nPlease check GitHub discussions/support for solutions https://github.com/GodsScion/Auto_job_applier_linkedIn \n                                   OR \nReach out in discord ( https://discord.gg/fFp7uUzWCY )'
    if isinstance(e,TimeoutError): 
        msg = "Couldn't download Chrome-driver. Set stealth_mode = False in config!"
    print_lg(msg)
    critical_error_log("In Opening Chrome", e)
    from pyautogui import alert
    alert(msg, "Error in opening chrome")
    try: driver.quit()
    except NameError: exit()

